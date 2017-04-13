# from apps import db
# from apps.api_server.utils.abstract_models import BaseModel
#
#
# class Payment(BaseModel):
#     __tablename__ = 'payments'
#     user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
#     basket_id = db.Column(db.Integer, db.ForeignKey('baskets.id'))
#     state = db.Column(db.Integer)
#
#     master = db.relationship('User', backref=db.backref('pay_info', lazy='dynamic'))
#     basket = db.relationship('Basket')
#
#     def __repr__(self):
#         return "<Payment %r>"
#
from sqlalchemy.ext.hybrid import hybrid_property

from apps.api_server.services.catalogue_service.models import CatalogueProductDetail, CatalogueProduct
from apps.api_server.utils.abstract_models import BaseModel
from apps import db
from flask_babel import lazy_gettext as _
# class Payment(BaseModel):
#     pass
#
# class PaymentMethod(BaseModel):
#
#     __tablename__ = 'payment_method'
#
#     """
#     1 : paypal
#     2 : Alipay
#     3 : 무통
#     """
#     name = db.Column(db.String(60))
#     dd = db.Column(db.Integer())
#
#     def __repr__(self):
#         return '<PaymentMethod %r>' % self.name


class Order(BaseModel):
    """
    주문을 하면 이 테이블에 들어간다
    """
    __tablename__ = 'order'

    currency = db.Column(db.String(20))
    subtotal = db.Column(db.DECIMAL(10, 2))
    shipping_fee = db.Column(db.DECIMAL(10, 2))
    total= db.Column(db.DECIMAL(10, 2))

    shipping_method = db.Column(db.String(65))

    """
    0: 주문 완료
    1: 결제 완료 (배송준비)
    2: 배송 중
    3: 배송 완료
    4: 환불 신청
    5: 환불 완료
    """
    order_state = db.Column(db.Integer, default=0)
    user_email = db.Column(db.String(255)) # shipping_email
    name = db.Column(db.String(65)) # shipping name

    billing_iso_3166_country = db.Column(db.String(2), db.ForeignKey('address_country.iso_3166_1_a2'))
    billing_state = db.Column(db.String(80))
    billing_city = db.Column(db.String(80))
    billing_line1 = db.Column(db.String(80))
    billing_line2 = db.Column(db.String(80))

    shipping_iso_3166_country = db.Column(db.String(2),db.ForeignKey('address_country.iso_3166_1_a2'))
    shipping_state = db.Column(db.String(80))
    shipping_city = db.Column(db.String(80))
    shipping_line1 = db.Column(db.String(80))
    shipping_line2 = db.Column(db.String(80))

    message = db.Column(db.String(255))
    payment_method = db.Column(db.String(20))

    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('order', lazy='dynamic'))

    def __repr__(self):
        return '<Order %r>' % self.id

    # @hybrid_property
    # def get_product_id(self):
    #     for x in self.order_line :
    #         return x.product_id
    #
    # @hybrid_property
    # def get_product_name(self):
    #     for x in self.order_line :
    #         cat = CatalogueProductDetail.query.filter(CatalogueProductDetail.product_code_id==x.product_id).all()
    #         for xx in cat:
    #             return xx.get_name()

    @hybrid_property
    def get_order_number(self):
        return 10000 + self.id

    @hybrid_property
    def get_userid(self):
        return self.user_id
        # @hybrid_property
        # def get_order_id(self):
        #     return self.order_id


class OrderLineItem(db.Model):
    """
    제품과 오더를 연결하는 모델입니다.
    """
    __tablename__ = "order_association"

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    product_id = db.Column(db.Integer, db.ForeignKey('catalogue_product.id'), primary_key=True)  # 제품 id
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))  # 제품 id
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)  # cart id
    quantity = db.Column(db.Integer)  # 제품의 양
    status = db.Column(db.Integer, default=0)

    order = db.relationship('Order', backref=db.backref('order_line', lazy='dynamic',
                                                        cascade="save-update, merge, "
                                                                "delete, delete-orphan"))
    product = db.relationship("CatalogueProduct", backref=db.backref('order_line', uselist=False,
                                                                     cascade="save-update, merge, "
                                                                             "delete, delete-orphan"))


    def __repr__(self):
        return '<OrderLineItem %r>' % self.order_id

    @hybrid_property
    def get_order_number(self):
        return 10000 + self.order_id

    @hybrid_property
    def get_product_name(self):
        cat = CatalogueProductDetail.query.filter(CatalogueProductDetail.product_code_id==self.product_id).all()
        for xx in cat:
            return xx.get_name()

    @hybrid_property
    def get_price(self):
        cat = CatalogueProduct.query.filter(CatalogueProduct.id==self.product_id).all()
        for xx in cat:
            price = xx.price * self.quantity
            return "{:,}".format(price)

    @hybrid_property
    def get_state(self):
        state =self.status
        # 주문 완료
        if state == 0:
            return _("Order Complete")

        # 출고 준비
        elif state == 1:
            return _("Ready to be shipped")

        # 배송 중
        elif state == 2:
            return _("Shipping in process")

        # 배송 완료 고객 물건 수령 완료
        elif state == 3:
            return _("All received")

        # 반품 신청
        elif state == 4:
            return _("Refund Request")

        # 반품 문건 받음
        elif state == 5:
            return _("Return received")

        # 반품 확인
        elif state == 6:
            return _("Refund Approved")

            # 반품 거절
        elif state == 7:
            return _("Refund Declined")

            # 반품 신청
        elif state == 8:
            return _("All refunded")




class Payment(BaseModel):

    __tablename__ = 'payment'

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    payment_method = db.Column(db.String(20))
    payment_unique_id = db.Column(db.String(100), unique=True)

    currency = db.Column(db.String(20))

    paid_in_total = db.Column(db.DECIMAL(10,2))

    total_refunded = db.Column(db.DECIMAL(10,2))

    def __repr__(self):
        return '<Payment %r>' % self.order_id



# 반품
class ProductReturn(BaseModel):
    """
    반품 테이
    """
    __tablename__ = "product_return"
    order_id = db.Column(db.Integer, db.ForeignKey('order_association.order_id'), primary_key=False)  # 제품 id
    product_id = db.Column(db.Integer, db.ForeignKey('order_association.product_id'), primary_key=False)  # cart id
    quantity = db.Column(db.Integer)  # 제품의 양
    exchangeORrefund = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15))
    email = db.Column(db.String(255)) # shipping_email
    message = db.Column(db.String(255),nullable=True)
    status = db.Column(db.Integer, default=0)


    def __repr__(self):
        return '<ProductReturn %r %r>' % (self.id, self.quantity)

    @hybrid_property
    def get_product_name(self):
        cat = CatalogueProductDetail.query.filter(CatalogueProductDetail.product_code_id==self.product_id).all()
        for xx in cat:
            return xx.get_name()


    @hybrid_property
    def get_state(self):
        state =self.status
        # Return Request
        if state == 0:
            return _("Return Requested")

        # Refund Ready
        elif state == 1:
            return _("Refund Ready")

        # Exchange Ready
        elif state == 2:
            return _("Exchange Ready")

        # Shipping in process
        elif state == 3:
            return _("Shipping in process")

        # Refunded
        elif state == 4:
            return _("Refunded")

        # Exchanged
        elif state == 5:
            return _("Exchanged")


    @hybrid_property
    def get_exchangeORrefund(self):
        exchangeORrefund =self.exchangeORrefund
        # Exchange
        if exchangeORrefund == 'EX':
            return _("Exchange")

        # Refund
        elif exchangeORrefund == 'RE':
            return _("Refund")

    @hybrid_property
    def get_productReturnId(self):
        return 2000+self.id