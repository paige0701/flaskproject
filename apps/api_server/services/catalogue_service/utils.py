from sqlalchemy.exc import IntegrityError

from apps import db, app
from apps.api_server.payment.models import ProductReturn
from apps.api_server.services.catalogue_service.models import CatalogueCategory, CatalogueCategoryDetail, \
    CatalogueProduct, CatalogueProductCart, CatalogueLineItem
from flask import logging
from apps.extensions import user_datastore

LANG_CHOICES = app.config['LANG_CHOICES']
STRUCTURE_CHOICES = app.config['PRODUCT_STRUCTURE_CHOICES']


def make_category(category_code, slug=None, depth=None, image=None, parent=[]):
    category = CatalogueCategory.get_category_with_code(category_code)
    print("AA")
    print(category)
    if not category:
        print("DD")
        # 카테고리가 존재하지 않으면
        try:
            category = CatalogueCategory(category_code=category_code, slug=slug, depth=depth, image=image,
                                         parent=parent)
            print(category)
            print("O")
            db.session.add(category)
            db.session.commit()
            return category
        except:
            db.session.rollback()
            category = None
    return category


def make_category_detail(category_code, name, description, lang_code):
    category = CatalogueCategory.get_category_with_code(category_code)

    if name is None and description is None and lang_code is None:
        # 반드시 있어야 하는 것들
        return None

    if not lang_code in LANG_CHOICES:
        # 허락된 LANG_CODE가 아닐때
        return None

    if category is None:
        # 카테고리 없음
        return None

    else:
        category_detail = CatalogueCategoryDetail(name=name, description=description, lang_code=lang_code,
                                                  category_code_id=category.id)
        db.session.add(category_detail)
        db.session.commit()
        return category_detail


def make_category_with_detail(category_code, name, description, lang_code,
                              slug=None, depth=None, image=None, parent=[]):
    category = make_category(category_code, slug, depth, image, parent)
    if category is None:
        # 카테고리 생성중 오류
        return None
    else:
        category_detail = make_category_detail(category_code, name, description, lang_code)
        db.session.add(category_detail)
        db.session.commit()
        return category, category_detail


def make_product(category_id, type_id, upc, price, currency="KRW", parent_id=None, structure='Standalone',
                 quantity=0):
    """
    주어진 category_id에 product를 넣음

    :param category_id: Required
    :param type_id: Required
    :param upc: Required
    :param price: Required
    :param currency: Required (default ="KRW")
    :param parent_id: Option (Structure: "Standalone" -> None)
    :param structure: Required ( default = "Standalone")
    :param quantity: Required(default = 0)
    :return:
    """

    product = CatalogueProduct.get_prod_upc(upc)

    if product is None:

        if category_id is None:
            return None
        if type_id is None:
            return None
        if upc is None:
            return None
        if price is None:
            return None
        if structure not in STRUCTURE_CHOICES:
            return None

        product = CatalogueProduct(category_id=category_id, type_id=type_id, upc=upc, price=price, currency=currency,
                                   parent_id=parent_id, structure=structure, quantity=quantity)

        db.session.add(product)
        db.session.commit()

    return product

#
#
# def make_product_with_detail(category_id, name, description, lang_code, product_id, type_id, upc, price, currency="KRW",
#                              parent_id=None, structure='Standalone', quantity=0, is_display=False):
#     prod = make_product(category_id, type_id, upc, price, currency, parent_id, structure, quantity)
#     if prod is None:
#         print("product를 생성하거나 Parameter에 문제가 있습니다.")
#         return None
# prod_detail = CatalogueProduct(category_id=category_id, type_id=type_id, upc=upc, price=price, currency=currency,
#                                parent_id=parent_id, structure=structure, quantity=quantity)
#
# name = db.Column(db.String(100), index=True, nullable=False)
# description = db.Column(db.Text())  # 설명
#
# lang_code = db.Column(db.CHAR(5), index=True)  # Language Code
#
# product_code_id = db.Column(db.Integer, db.ForeignKey('catalogue_product.id'))
# product_code = db.relationship('CatalogueProduct', backref=db.backref('product_detail', lazy='dynamic'))
#
# is_display = db.Column(db.Boolean, default=False)  # 배포 여부


# product 쪽 장바구니에 넣는다
def add_cart(user_id,status,product_id,quantity):

    cart = CatalogueProductCart.query.filter_by(user_id=user_id, status='Open').first()
    if cart is None:
        cart = CatalogueProductCart(user_id=user_id, status='Open')
        line = CatalogueLineItem(cart=cart, product_id = product_id, quantity=quantity)
        db.session.add(cart)
        db.session.add(line)
        db.session.commit()
    else:
        # print("cart is duplicated")

        line = CatalogueLineItem.query.filter_by(cart_id=cart.id,product_id=product_id).first()
        if line is None :
            cart = CatalogueLineItem(cart=cart, product_id=product_id, quantity=quantity)
            db.session.add(cart)

        else:
            line.quantity += int(quantity)

        db.session.commit()

    return line, cart


# product_cart update 하기
def update_cart(user_id,status,product_id,quantity):

    cart = CatalogueProductCart.query.filter_by(user_id=user_id, status='Open').first()
    if cart is None:
        cart = CatalogueProductCart(user_id=user_id, status='Open')
        line = CatalogueLineItem(cart=cart, product_id = product_id, quantity=quantity)
        db.session.add(cart)
        db.session.add(line)
        db.session.commit()
    else:
        line = CatalogueLineItem.query.filter_by(cart_id=cart.id,product_id=product_id).first()
        if line is None :
            cart = CatalogueLineItem(cart=cart, product_id=product_id, quantity=quantity)
            db.session.add(cart)

        else:
            line.quantity = quantity
            print(line.quantity)
            db.session.add(line)
            db.session.commit()

    return line, cart


def delete_cart(user_id):

    cart = CatalogueProductCart.query.filter_by(user_id=user_id).first()

    if cart:
        cart = CatalogueProductCart.query.filter(CatalogueCategory.userid == user_id).first()

    #     line = CatalogueLineItem(cart=cart, product_id = product_id, quantity=quantity)
    #     db.session.add(cart)
    #     db.session.add(line)
    #     db.session.commit()
    # else:
    #     line = CatalogueLineItem.query.filter_by(cart_id=cart.id).first()
    #     if line is None :
    #         cart = CatalogueLineItem(cart=cart, product_id=product_id, quantity=quantity)
    #         db.session.add(cart)
    #
    #     else:
    #         line.quantity = quantity
    #         print(line.quantity)
    #         db.session.add(line)
    #         db.session.commit()

    return cart


def makeProductReturn(email,quantity,product_id,order_id,contact_number,message,refund_reason,exchange_refund):

    productReturn = ProductReturn(email=email,product_id=product_id,order_id=order_id,contact_number=contact_number,
                                  exchangeORrefund=exchange_refund,
                                  reason=refund_reason,quantity=quantity, message=message)


    return productReturn
