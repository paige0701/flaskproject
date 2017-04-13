import enum

from decimal import Decimal
from sqlalchemy import desc
from sqlalchemy.orm.query import Query as _query

from apps import db, app
from apps.api_server.utils.abstract_models import BaseModel
from apps.api_server.auth.models import User
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from flask_babel import lazy_gettext as _

from apps.settings import BaseConfig

LANG_CHOICES = BaseConfig.LANG_CHOICES


class CatalogueCategory(BaseModel):
    """
    카테고리코드는 반드시 존재해야 합니다.
    카테고리를 저장합니다.
    카테고리별로 parent-child 관계를 맺을 수 있습니다.
    """
    __tablename__ = 'catalogue_category'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    category_code = db.Column(db.String(16), unique=True, nullable=False)  # 같은 카테고리 코드로 구분(code로 구분)
    # category_code = db.Column(db.String(16), unique=True)  # 같은 카테고리 코드로 구분(code로 구분)

    parent_id = db.Column(db.Integer, db.ForeignKey('catalogue_category.id'))
    parent = db.relationship('CatalogueCategory', backref=db.backref('children', remote_side=[id]))  # 부모 카테고리

    depth = db.Column(db.Integer, default=0)  # 깊이 ( 일반적으로 부모 카테고리의 갯수를 의미한다.)
    image = db.Column(db.String(255))

    categories = db.relationship('CatalogueCategoryDetail')

    is_display = db.Column(db.Boolean, default=True)

    _full_name_separator = '>'

    def get_ancestors_and_self(self):
        """
        Gets ancestors and includes itself. Use treebeard's get_ancestors
        if you don't want to include the category itself. It's a separate
        function as it's commonly used in templates.
        """
        return list(self.get_ancestors()).insert(0, self)

    def get_name(self, lang_code='en'):
        for category in self.categories:
            if category.lang_code == lang_code:
                return category.name

        return None

    def get_parent(self):
        """
        Gets Parent
        :return:
        """
        if self.depth > 0:
            return self.parent
        elif self.depth == 0:
            return None
        else:
            raise ValueError("잘못된 값이 나왔습니다. Category의 depth는 0 보다 작을 수 없습니다.")

    def get_ancestors(self, ancestors_list=None):
        """
        :param ancestors_list: recursive를 위한 재귀값

        :returns: A queryset containing the current node object's ancestors,
                starting by the root node and descending to the parent.
                재귀로 호출한다. ancestors_list depth가 낮을수록 앞에 위치하도록 한다.
        """
        if ancestors_list is None:
            ancestors_list = []

        parent = self.get_parent()

        if parent is not None:
            ancestors_list.insert(0, parent)
            parent.get_ancestors(ancestors_list)

        return ancestors_list

    @classmethod
    def get_category(cls, category_code):
        """
        category를 가져온다.
        :param category_code: 카테고리 코드
        :return: 카테고리
        """
        category = cls.query.filter_by(category_code=category_code).first()
        if category is None:
            raise ValueError('해당 카테고리가 없습니다.')
        return category

    @classmethod
    def get_category_with_detail(cls, category_code, lang_code):
        """
        category와 detail을 함께 가져온다.

        :param category_code: 카테고리 코드
        :param lang_code: 언어 코드
        :return: category_detail
        // 만약 입력이 잘못되었다면 Error발생
        """
        category = cls.get_category(category_code)

        category_detail = category.category_detail.filter_by(lang_code=lang_code).first()

        if category_detail is not None:
            return category_detail
        else:
            raise ValueError('해당 lang_code에 맞는 Category Detail이 없습니다.')

    @hybrid_property
    def get_products(self, page=0, list_size=50):
        """
        Category에 연결된 products를 가져온다.

        :param page: page 수
        :param list_size: 한 page에 보이는 row 수

        :return:
        """

        return self.products.order_by(desc(CatalogueProduct.created_at)).limit(50).all()

    @property
    def get_category_lang(self):
        lang = []
        for category in self.categories:
            lang.append(category.lang_code)
        return lang

    @property
    def get_need_lang(self):
        lang = list(LANG_CHOICES.keys())
        for category in self.categories:
            if category.lang_code in lang:
                lang.remove(category.lang_code)
        return lang

    @hybrid_property
    def get_image(self):
        return self.image

    def __repr__(self):
        return "<Catalogue Category code: %r>" % self.category_code


class CatalogueCategoryDetail(BaseModel):
    """
    A product category. Merely used for navigational purposes; has no
    effects on business logic.

    카테고리에 대한 내용을 저장합니다.
    """
    __tablename__ = 'catalogue_category_detail'
    name = db.Column(db.String(100), unique=True, index=True)  # 이름
    description = db.Column(db.String(100))  # 설명

    category_code_id = db.Column(db.Integer, db.ForeignKey('catalogue_category.id'))
    category_code = db.relationship('CatalogueCategory', backref=db.backref('category_detail', lazy='dynamic'))

    lang_code = db.Column(db.CHAR(5), index=True)  # Language Code

    def __repr__(self):
        return '<Category Detail %r (%r)>' % (self.name, self.lang_code)

    def check_lang_code(self, lang_code):
        if self.lang_code not in LANG_CHOICES:
            return ValueError(('%s 는 허락된 Language code가 아닙니다' % lang_code))
        else:
            return True

    @hybrid_property
    def full_name(self):
        """
        Returns a string representation of the category and it's ancestors,
        e.g. 'Books > Non-fiction > Essential programming'.

        It's rarely used in Oscar's codebase, but used to be stored as a
        CharField and is hence kept for backwards compatibility. It's also
        sufficiently useful to keep around.
        """
        names = [category.name for category in self.get_ancestors_and_self()]
        return self._full_name_separator.join(names)


# Product // Product Detail
class CatalogueProduct(BaseModel):
    """
    catalogue 제품들을 저장합니다.

    The base product object

    There's three kinds of products; they're distinguished by the structure
    field.

    - A stand alone product. Regular product that lives by itself.
    - A child product. All child products have a parent product. They're a
      specific version of the parent.
    - A parent product. It essentially represents a set of products.

    An example could be a yoga course, which is a parent product. The different
    times/locations of the courses would be associated with the child products.
    """
    __tablename__ = 'catalogue_product'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    structure = db.Column(db.CHAR(10), default='Standalone')
    upc = db.Column(db.String(64), unique=True, nullable=False)

    category_id = db.Column(db.Integer(), db.ForeignKey('catalogue_category.id'))  # category와 관계
    category = db.relationship('CatalogueCategory', foreign_keys=[category_id],
                               backref=db.backref('products', lazy='dynamic'))

    parent_id = db.Column(db.Integer, db.ForeignKey('catalogue_product.id'))
    parent = db.relationship('CatalogueProduct', backref=db.backref('children', remote_side=[id]))

    price = db.Column(db.DECIMAL, nullable=False)
    currency = db.Column(db.CHAR(3), default='KRW')

    type_id = db.Column(db.Integer, db.ForeignKey('catalogue_product_type.id'), nullable=True)
    type = db.relationship('CatalogueProductType', foreign_keys=[type_id],
                           backref=db.backref('products', lazy='dynamic'))

    quantity = db.Column(db.Integer())  # 현재 재고량

    attribute = db.relationship("CatalogueProductAttribute", secondary='attribute_association',
                                backref=db.backref('product', lazy='dynamic'))

    def get_product_detail(self, lang_code='en'):
        return self.product_detail.filter_by(lang_code=lang_code).first()

    @hybrid_property
    def get_product_description(self):
        name = self.product_detail

        return name.first().description

    def get_category(self, lang_code='en'):
        return self.category

    @property
    def get_product_lang(self):
        lang = []
        for product in self.product_detail:
            lang.append(product.lang_code)
        return lang

    @property
    def get_need_lang(self):
        lang = list(LANG_CHOICES.keys())
        for product in self.product_detail:
            if product.lang_code in lang:
                lang.remove(product.lang_code)
        return lang

    @classmethod
    def get_prod_upc(cls, upc):
        return cls.query.filter_by(upc=upc).first()

    @hybrid_property
    def get_upc(self):
        return self.upc

    @classmethod
    def available_structure(cls):
        return PRODUCT_STRUCTURE_CHOICES

    @hybrid_property
    def is_standalone(self):
        return self.structure == 'Standalone'

    @hybrid_property
    def is_parent(self):
        return self.structure == 'Parent'

    @hybrid_property
    def is_child(self):
        return self.structure == 'Child'

    def __repr__(self):
        return '<CatalogueProduct %r>' % self.id

    @hybrid_property
    def get_thumbnail_image(self):
        images = self.get_images
        if images is None:
            return "product/not_found.jpg"
        else:
            for image in images:
                if image.is_thumbnail:
                    return image.url
            return "product/not_found.jpg"


    @hybrid_property
    def get_images(self):
        if self.images is None:
            return "not_found_image.jpg"
        return self.images.all()

    @hybrid_property
    def get_title(self):
        """
        수정 필요 (babel 껴서)
        :return:
        """
        name = self.product_detail
        return name.first().get_name()

    @hybrid_property
    def get_usd_price(self):
        """

        :return:
         :type: round
        """
        if self.currency =='KRW':
            return round(self.price/1100,2)
        return None

    @hybrid_property
    def product_price_separated(self):
        price = self.price
        return "{:,}".format(price)



class CatalogueProductDetail(BaseModel):
    """
    catalogue Product에 대한 설명들
    이름
    설명
    lang_code등이 들어갑니다.
    """

    __tablename__ = 'catalogue_product_detail'

    name = db.Column(db.String(100), index=True, nullable=False)
    description = db.Column(db.Text())  # 설명

    lang_code = db.Column(db.CHAR(5), index=True)  # Language Code

    product_code_id = db.Column(db.Integer, db.ForeignKey('catalogue_product.id'))
    product_code = db.relationship('CatalogueProduct', backref=db.backref('product_detail', lazy='dynamic'))

    is_display = db.Column(db.Boolean, default=False)  # 배포 여부

    def __repr__(self):
        return '<CatalogueProductDetail %r>' % self.name

    def get_name(self):
        return self.name


class CatalogueProductType(BaseModel):
    """
    제품의 type을 정합니다. 이는 해당 카테고리에 종속되지 않고 배송 여부등을 결정합니다.
    """
    __tablename__ = 'catalogue_product_type'
    name = db.Column(db.String(80))
    description = db.Column(db.String(255))

    #: Some product type don't require shipping (eg digital products) - we use
    #: this field to take some shortcuts in the checkout.
    requires_shipping = db.Column(db.Boolean, default=True)  # 배송 여부
    track_stock = db.Column(db.Boolean, default=True)  # 재고 추적 여부


class CatalogueProudctImage(BaseModel):
    """
    제품의 이미지를 저장합니다. 제품과 관계를 맺고 있습니다.
    """
    __tablename__ = 'catalogue_product_image'

    url = db.Column(db.String(255))

    is_thumbnail = db.Column(db.Boolean, default=False)

    product_id = db.Column(db.Integer(), db.ForeignKey('catalogue_product.id'))
    product = db.relationship('CatalogueProduct', foreign_keys=[product_id],
                              backref=db.backref('images', lazy='dynamic'))

    def __repr__(self):
        return '<CatalogueProudctImage %r>' % self.url


class CatalogueProductOption(BaseModel):
    """
    제품 및 타입의 옵션을 정합니다.
    """
    __tablename__ = 'catalogue_product_option'

    name = db.Column(db.String(80))
    description = db.Column(db.String(255))
    additional_price = db.Column(db.DECIMAL(10))


class CatalogueLineItem(BaseModel):
    """
    제품과 카트를 연결하는 모델입니다.
    """
    __tablename__ = "catalogue_association"

    product_id = db.Column(db.Integer, db.ForeignKey('catalogue_product.id'), primary_key=True)  # 제품 id
    cart_id = db.Column(db.Integer, db.ForeignKey('catalogue_product_cart.id'), primary_key=True)  # cart id
    quantity = db.Column(db.Integer)  # 제품의 양

    # order = relationship("Order", backref=backref("order_products", cascade="all, delete-orphan"))
    # product = relationship("Product", backref=backref("order_products", cascade="all, delete-orphan"))

    cart = db.relationship('CatalogueProductCart', backref=db.backref('line_item', cascade="save-update, merge, "
                                                                                           "delete, delete-orphan"))

    product = db.relationship("CatalogueProduct", backref=db.backref('line_item', cascade="save-update, merge, "
                                                                                          "delete, delete-orphan"))

    # 하나의 상품에 대한 가격 == 2개 * 가격
    def total_price_separated(self):
        total = self.quantity * self.product.price
        # total = int(price)*int(quantity)

        return "{:,}".format(total)

    def total_price(self):
        total = self.quantity * self.product.price
        # total = int(price)*int(quantity)

        return total

    def get_product_id(self):
        return self.product_id


class CatalogueProductCart(BaseModel):
    """
        Catalogue의 카트입니다.
    """
    __tablename__ = 'catalogue_product_cart'

    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    products = db.relationship("CatalogueProduct", secondary='catalogue_association',
                               backref=db.backref('cart', lazy='dynamic'))

    owner = db.relationship('User', backref=db.backref('catalogue_cart', lazy='dynamic'))

    # Cart statuses(상태)
    # - Frozen is for when a basket is in the process of being submitted
    #   and we need to prevent any changes to it.

    status = db.Column(db.CHAR(10), nullable=False)

    # A basket can have many vouchers attached to it.  However, it is common
    # for sites to only allow one voucher per basket - this will need to be
    # enforced in the project's codebase.
    """
    보류
    """
    # vouchers = models.ManyToManyField(
    #         'voucher.Voucher', verbose_name=_("Vouchers"), blank=True)

    date_merged = db.Column(db.DateTime, nullable=True)

    # Only if a basket is in one of these statuses can it be edited
    """
    보류
    """

    # editable_statuses = (STATUS_CHOICES.Open, STATUS_CHOICES.Saved)

    def set_status(self, status):
        if status not in CART_STATUS_CHOICES:
            raise ValueError(("%s 는 입력될 수 없는 State 입니다." % status))
        else:
            self.status = status
        return status


        #
        # class CatalgoueProductOption(BaseModel):
        #     """
        #     제품의 옵션을 정합니다
        #     예를들어) 옷 한벌에 여러가지 색상이 있는경우에 추가 할 수 있습니다.
        #     """
        #     __tablename__ = 'catalogue_product_option'
        #
        #     name = db.Column(db.String(80))
        #     description = db.Column(db.String(255))
        #     additional_price = db.Column(db.DECIMAL(10))
        #

    # 장바구니 가격을 말한다
    @hybrid_property
    def get_total_amount(self):
        total = 0
        for item in self.line_item:
            total += item.total_price()
        return total

    @hybrid_property
    def get_total_amount_separated(self):
        total = 0
        for item in self.line_item:
            total += item.total_price()
        return "{:,}".format(total)

    # 배송비
    @hybrid_property
    def shipping_fee(self):
        # print("dd")
        # print(self.get_total_amount)
        if self.get_total_amount > 30000:
            return 0
        elif self.get_total_amount == 0:
            return 0
        else:
            return 3000

    # 배송비
    @hybrid_property
    def shipping_fee_separated(self):
        # print("dd")
        # print(self.get_total_amount)
        if self.get_total_amount > 30000:
            return 0
        elif self.get_total_amount == 0:
            return 0
        else:
            return "{:,}".format(3000)

    # 배송비 포함 총 가격
    @property
    def total_amount_with_shipping(self):
        total = self.shipping_fee + self.get_total_amount
        return total

    # 배송비 포함 총 가격
    @property
    def total_amount_with_shipping_separated(self):
        total = self.shipping_fee + self.get_total_amount
        return "{:,}".format(total)

    # 장바구니에서 상품을 지운다.
    def remove_line_item(self, remove_list):
        # if not remove_list in self.line_item:
        #     return None
        line_items = self.line_item.copy()
        for line in line_items:
            print(str(line.id))
            if str(line.product_id) in remove_list:
                self.line_item.remove(line)
        return True


class CatalogueProductAttribute(BaseModel):
    """
    Catalogue product Attribute
    """
    __tablename__ = 'catalogue_product_attribute'
    category_code_id = db.Column(db.Integer, db.ForeignKey('catalogue_category.id'))
    product_attribute = db.Column(db.String(80))


class CatalogueAttributeAssociation(BaseModel):

    __tablename__ = "attribute_association"

    product_id = db.Column(db.Integer, db.ForeignKey('catalogue_product.id'))
    catalogue_product_attribute_id = db.Column(db.Integer, db.ForeignKey('catalogue_product_attribute.id'))
    value = db.Column(db.String(80))

    attribute = db.relationship('CatalogueProductAttribute', backref=db.backref('attribute', lazy='dynamic'))

    @hybrid_property
    def get_attributeName(self):
        return CatalogueProductAttribute.product_attribute

