from sqlalchemy import func, asc, desc
from sqlalchemy.ext.hybrid import hybrid_property

from apps import db
from apps.api_server.address.models import UserAddress
from apps.api_server.utils.abstract_models import BaseModel
from flask_babel import lazy_gettext as _, format_decimal


class WirelessSimOrder(BaseModel):
    """
        심카드 주문
    """

    __tablename__ = 'wireless_sim_order'
    __mapper_args__ = {'order_by': desc('id')}

    __order_number_generator = 123576

    sim_type = db.Column(db.CHAR(2))  # 마이크로 나노 여부
    phone_type = db.Column(db.String(30))  # 폰 종류
    sim_number = db.Column(db.String(20))  # sim 번호

    shipping_address_id = db.Column(db.ForeignKey('address_user_address.id'))
    shipping_address = db.relationship('UserAddress')

    shipping_message = db.Column(db.String(255))
    payment_method = db.Column(db.String(20))

    """
    0: 주문 완료
    1: 결제 완료 (배송준비)
    2: 배송 중
    3: 배송 완료
    4: 환불 신청
    5: 환불 완료
    """
    order_state = db.Column(db.Integer, default=0)

    currency = db.Column(db.String(3))
    price = db.Column(db.DECIMAL)

    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), index=True)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('sim_order', lazy='dynamic'))

    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    payment = db.relationship('Payment', foreign_keys=payment_id, backref=db.backref('sim_order', lazy='dynamic'))

    is_actviated = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<SimOrder %d>" % self.order_number

    @hybrid_property
    def get_order_state(self):
        state = self.order_state
        if state == 0:
            return "Order Completed"
        elif state == 1:
            return "Payment Completed"
        elif state == 2:
            return "Shipping"
        elif state == 3:
            return "Shipping Completed"
        elif state == 4:
            return "Refund Apply"
        elif state == 5:
            return "Refund Completed"

    def payment_complete(self):
        self.order_state = 1

    def shipping_start(self):
        if self.order_state != 1:
            return False
        self.order_state = 2

    @hybrid_property
    def full_name(self):
        return "%s %s" % (self.shipping_address.first_name + self.shipping_address.last_name)

    @hybrid_property
    def order_number(self):
        return self.id + self.__order_number_generator

    @classmethod
    def get_with_order_number(cls, order_number):
        record_id = order_number - cls.__order_number_generator
        return cls.query.filter_by(id=record_id).first()

    @hybrid_property
    def full_address(self):
        return self.shipping_address.full_address

    @staticmethod
    def make_first_order(dict_data, price=None, currency=None, user=None, payment_method=None):
        """
        shipping_address와 이와 연결된 order를 생성
        """
        shipping_address = UserAddress.make_shipping_address(dict_data, user=user, is_main_shipping=True)
        db.session.add(shipping_address)
        db.session.commit()

        wireless_order = WirelessSimOrder(
                phone_type=dict_data['phone_type'],
                shipping_message=dict_data['message'],
                order_state=0,
                price=price,
                currency=currency,
                user=user,
                payment_method=payment_method,
                shipping_address=shipping_address
        )
        db.session.add(wireless_order)
        db.session.commit()

        return wireless_order

    def set_sim_number(self, sim_number):
        # sim number를 세팅합니다.
        self.sim_number = sim_number
        return sim_number

    @hybrid_property
    def full_name(self):
        return "%s %s" % (self.shipping_address.first_name, self.shipping_address.last_name)

    @hybrid_property
    def shipping_email(self):
        return self.shipping_address.email

    @hybrid_property
    def user_email(self):
        return self.user.email


class WirelessSimActivateModel(BaseModel):
    """
    심카드 개통 여부
    """
    __tablename__ = 'wireless_sim_activate'
    __mapper_args__ = {'order_by': desc('created_at')}

    STATE = dict(
            ORDER=0,
            ACTIVATION=1,
            CANNOT=2,
            DEACTIVATION=3
    )

    english_name = db.Column(db.String(50))  # 여권상 이름
    id_number = db.Column(db.String(30))  # 여권/외국인등록증 번호
    birthday = db.Column(db.CHAR(8))  # 생년월일 - 년
    contact_no = db.Column(db.String(16))  # 연락 가능 전화번호
    address = db.Column(db.String(255))  # 주소

    nationality_iso_3166_country = db.Column(db.CHAR(2), db.ForeignKey('address_country.iso_3166_1_a2'))  # 국적
    nationality = db.relationship('Country', foreign_keys=[nationality_iso_3166_country])

    call_plan = db.Column(db.String(10))  # 신청 요금제
    phone_model = db.Column(db.String(30))  # 휴대폰 모델(eg. Iphone5)
    imei = db.Column(db.String(30))  # imei 번호
    sim_number = db.Column(db.String(20))  # sim 일련번호

    passport_img = db.Column(db.String(255))  # 여권/외국인등록증 사진

    sim_type = db.Column(db.CHAR(2))  # sim 종류 4g/3g

    active_number = db.Column(db.String(16))  # 개통된 번호

    status = db.Column(db.Integer)  # 상태
    """
    ***[status]***
    0. 개통 신청
    1. 개통 완료(충전가능)
    2. 개통 불가
    3. 사용 기간 만료(폰 해지)
    """

    status_description = db.Column(db.String(255))  # status에 대한 비고

    activate_date = db.Column(db.DateTime())  # 활성화 날짜
    deactivate_date = db.Column(db.DateTime())  # 비활성화 예정 날짜

    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), index=True)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('activated_sim', lazy='dynamic'))

    # @hybrid_property
    # def birthday(self):
    #     return "%s-%s-%s" % (self.birth_year, self.birth_month, self.birth_date)

    @hybrid_property
    def get_status(self):
        if self.status == 0:
            return _('Pending')
        elif self.status == 1:
            return _('Available')
        elif self.status == 2:
            return _('Can not Activation')
        elif self.status == 3:
            return _('Overed Period')

    @staticmethod
    def first_activation_inquiry(english_name, id_number, birthday, contact_no, address, nationality_3166, call_plan,
                                 phone_model, imei, sim_number, passport_img, user):
        first_status = 0
        return WirelessSimActivateModel(
                english_name=english_name, id_number=id_number, birthday=birthday, contact_no=contact_no,
                address=address,
                nationality_iso_3166_country=nationality_3166, call_plan=call_plan, phone_model=phone_model,
                imei=imei, sim_number=sim_number, passport_img=passport_img, user=user, status=first_status
        )

    @hybrid_property
    def get_active_number(self):
        if self.active_number:
            return "%s-%s-%s" % (self.active_number[1:4], self.active_number[4:8], self.active_number[8:12])
        else:
            return '-'

    @hybrid_property
    def get_status_description(self):
        if self.status_description:
            return self.status_description
        else:
            return '-'

    @hybrid_property
    def get_price_unit(self):
        if self.call_plan == '585':
            return 58500
        elif self.call_plan == '297':
            return 29700
        elif self.call_plan == 'payg':
            return 10000

    @hybrid_property
    def get_plan_type(self):
        if self.call_plan == 'payg':
            return 'PAYG PLAN'
        else:
            return 'FLAT PLAN'

    @hybrid_property
    def get_basic_info(self):
        return dict(
                call_plan=self.call_plan,
                status=self.get_status,
                status_description=self.get_status_description,
                active_number=self.get_active_number,
                price_unit=self.get_price_unit
        )

    @hybrid_property
    def get_call_plan(self):
        return self.call_plan


class WirelessRechargeModel(BaseModel):
    __tablename__ = 'wireless_recharge'
    __mapper_args__ = {'order_by': desc('created_at')}

    """
    0. 충전신청
    1. 결제 완료 (충전 대기)
    2. 충전완료
    3. 충전불가
    """
    _recharge_order_generator = 120473

    status = db.Column(db.Integer, default=0)
    status_description = db.Column(db.String(255))  # status에 대한 비고

    price = db.Column(db.DECIMAL)
    quantity = db.Column(db.Integer)

    currency = db.Column(db.String(3))
    payment_method = db.Column(db.String(20))

    activated_wireless_id = db.Column(db.Integer, db.ForeignKey('wireless_sim_activate.id'))
    activated_wireless = db.relationship('WirelessSimActivateModel', foreign_keys=[activated_wireless_id],
                                         backref=db.backref('sim_recharge', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), index=True)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('sim_recharge', lazy='dynamic'))

    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    payment = db.relationship('Payment', foreign_keys=payment_id, backref=db.backref('sim_recharge', lazy='dynamic'))

    @staticmethod
    def make_recharge_order(activated_wireless, price, quantity, currency, user, payment_method):
        # recharge_order = WirelessRecharge(
        #     status =
        # )
        recharge_order = WirelessRechargeModel(
                status=0,
                price=price,
                quantity=quantity,
                currency=currency,
                user=user,
                payment_method=payment_method,
                activated_wireless=activated_wireless
        )
        db.session.add(recharge_order)
        db.session.commit()

        return recharge_order

    @hybrid_property
    def order_number(self):
        return self._recharge_order_generator + self.id

    @classmethod
    def get_with_order_number(cls, order_number):
        record_id = order_number - cls._recharge_order_generator
        return cls.query.filter_by(id=record_id).first()

    def payment_complete(self):
        self.status = 1

    @hybrid_property
    def get_state(self):
        """
        0. 충전신청
        1. 결제 완료 (충전 대기)
        2. 충전완료
        3. 충전불가
        """
        if self.status == 0:
            return _('Payment Waiting')
        elif self.status == 1:
            return _('Pending Recharge')
        elif self.status == 2:
            return _('Complete')
        elif self.status == 3:
            return _('Can\'t Recharge')

    @hybrid_property
    def get_brief_info(self):
        activated = self.activated_wireless
        return dict(
                state=self.get_state,
                price=self.get_price,
                quantity=self.quantity,
                remark=self.get_status_description,
                active_number=activated.get_active_number,
                call_plan=activated.get_call_plan
        )

    @hybrid_property
    def get_status_description(self):
        if not self.status_description:
            return '-'
        return self.status_description

    @hybrid_property
    def get_price(self):
        return format_decimal(self.price)

def make_first_order(dict_data, price=None, currency=None, user=None, payment_method=None):
    """
    shipping_address와 이와 연결된 order를 생성
    """
    shipping_address = UserAddress.make_shipping_address(dict_data, user=user, is_main_shipping=True)
    db.session.add(shipping_address)
    db.session.commit()

    wireless_order = WirelessSimOrder(
            phone_type=dict_data['phone_type'],
            shipping_message=dict_data['message'],
            order_state=0,
            price=price,
            currency=currency,
            user=user,
            payment_method=payment_method,
            shipping_address=shipping_address
    )
    db.session.add(wireless_order)
    db.session.commit()

    return wireless_order
