from sqlalchemy.ext.hybrid import hybrid_property

from apps import app, db
from apps.api_server.utils.abstract_models import BaseModel

LANG_CHOICES = app.config['LANG_CHOICES'].copy()
PRODUCT_STRUCTURE_CHOICES = app.config['PRODUCT_STRUCTURE_CHOICES'].copy()
CART_STATUS_CHOICES = app.config['CART_STATUS_CHOICES'].copy()


class CrawlCategory(BaseModel):
    """
    <크롤링 카테고리>
     :var parent : 상위 카테고리 (backref: children 하위 카테고리)
     :var depth : 깊이 ( depth가 클 수록 하위 카테고리 )
     :var is_display : display 여부
    """

    __tablename__ = 'crawl_category'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    parent_id = db.Column(db.Integer, db.ForeignKey('crawl_category.id'))
    parent = db.relationship('CrawlCategory', backref=db.backref('children', remote_side=[id]))

    depth = db.Column(db.Integer, default=0)

    is_display = db.Column(db.Boolean, default=True)

    _full_name_separator = '>'

    def __repr__(self):
        return "<CrawlCategory %s %s>" % self.id

    @hybrid_property
    def category_code(self):
        return str(self.id * 3 + 11)


class CrawlCategoryDetail(BaseModel):
    """
    <크롤링 카테고리 detail>
     :var name : 카테고리 이름
     :var description : 카테고리 설명
     :var core_category : 중앙 카테고리
     :var lang_code : 언어 코드
    """

    __tablename__ = ' crawl_category_detail'
    name = db.Column(db.String(100), unique=True, index=True)
    description = db.Column(db.String(100))

    crawl_category_id = db.Column(db.Integer, db.ForeignKey('crawl_category.id'))
    core_category = db.relationship('CrawlCategory', backref=db.backref('crawl_category_detail', lazy='dynamic'))

    lang_code = db.Column(db.CHAR(5), index=True)

    def __repr__(self):
        return "<CrawlCategoryDetail %s %s>" % (self.name, self.lang_code)

    @hybrid_property
    def sibling_category(self):
        return self.core_category.crawl_category_detail.all()

    def get_category(self):
        return self.name, self.description


class CrawlProduct(BaseModel):
    """
    <크롤링 프로덕트>
     :var structure : Product 형식 (Standalone, parent, child)
     :var upc : UPC 고유 코드
     :var category : 속한 카테고리 (backref = crawl_product)
     :var parent : Standalone 이 아닐때 parent
     :var price : 가격
     :var currency : 화폐 코드
     :var source : 크롤링 페이지
     :var url : 크롤링 url
    """
    __tablename__ = 'crawl_product'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    structure = db.Column(db.CHAR(10), default='Standalone')
    upc = db.Column(db.String(64), unique=True, nullable=False)

    category_id = db.Column(db.Integer(), db.ForeignKey('crawl_category.id'))
    category = db.relationship('CrawlCategory', foreign_keys=[category_id],
                               backref=db.backref('crawl_products', lazy='dynamic'))

    parent_id = db.Column(db.Integer, db.ForeignKey('crawl_product.id'))
    parent = db.relationship('CrawlProduct', backref=db.backref('children', remote_side=[id]))

    price = db.Column(db.DECIMAL, nullable=False)
    currency = db.Column(db.CHAR(3), default='KRW')

    source = db.Column(db.String(20))
    url = db.Column(db.String(255))

    def __repr__(self):
        return "<Crawl Product %s>" % self.upc


class CrawlProductDetail(BaseModel):
    """
    <크롤링 프로덕트 디테일>
     :var name : 제품 이름
     :var description : 제품 설명
     :var lang_code : 제품 언어코드
     :var core_product : 루트 제품 (backref crawl_product_detail)
     :var is_display : display 여부
    """
    __tablename__ = 'crawl_product_detail'

    name = db.Column(db.String(100), index=True, nullable=False)
    description = db.Column(db.Text())  # 설명

    lang_code = db.Column(db.CHAR(5), index=True)  # Language Code

    crawl_product_id = db.Column(db.Integer, db.ForeignKey('crawl_product.id'))
    core_product = db.relationship('CrawlProduct', backref=db.backref('crawl_product_detail', lazy='dynamic'))

    is_display = db.Column(db.Boolean, default=False)  # 배포 여부

    def __repr__(self):
        return "<CrawlProductDetail %s %s>" % self.name, self.lang_code


