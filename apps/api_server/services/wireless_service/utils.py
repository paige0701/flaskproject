from apps import db
from apps.api_server.services.wireless_service.models import SimcardOrder, SimcardPayment, WirelessSimcardProduct, \
    WirelessSimActivate, WirelessSimActivateModel
from flask_security import current_user


def get_sim_total_amount():
    # (가지고 있고, 판매된) 전체 심 개수 반환
    return WirelessSimcardProduct.query.count()


def get_sim_type_amount(sim_type):
    # 타입별 (가지고 있고, 판매된) 전체 심 개수 반환
    # type: 3G or 4G
    return WirelessSimcardProduct.query.filter_by(sim_type=sim_type).count()


def get_have_sim_total_amount():
    # 가지고 있는 심 개수 반환
    return WirelessSimcardProduct.query.filter_by(is_sold=False).count()


def get_have_sim_type_amount(sim_type):
    # 타입별 가지고 있는 심 개수 반환
    # type: 3G or 4G
    return WirelessSimcardProduct.query.filter_by(is_sold=False).filter_by(sim_type=sim_type).count()


def receiving_3g_sim(sim_number):
    """
    3g sim 입고
    """
    product = WirelessSimcardProduct(sim_type="3G", sim_number=sim_number)
    db.session.add(product)
    db.session.commit()
    return product


def receiving_4g_sim(sim_number):
    """
    4g sim 입고
    """
    product = WirelessSimcardProduct(sim_type="4G", sim_number=sim_number)
    db.session.add(product)
    db.session.commit()
    return product


def sale_4g_sim(sim_number):
    """
    4g sim 출고
    """
    product = WirelessSimcardProduct.query.filter_by(sim_type="4G").filter_by(sim_number=sim_number).first()
    if product is not None:
        # 업데이트
        product.is_sold = True
        db.session.commit()
        return product
    else:
        return None


def sale_3g_sim(sim_number):
    """
        3g sim 출고
    """
    product = WirelessSimcardProduct.query.filter_by(sim_type="3G").filter_by(sim_number=sim_number).first()
    if product is not None:
        # 업데이트
        product.is_sold = True
        db.session.commit()
        return product
    else:
        return None


def customer_order_simcard(rcv_address1, rcv_address2, rcv_address3, rcv_extra_address, rcv_date, user_email,
                           phone_type):
    """
    order sim 카드
    """
    sim_order = SimcardOrder(rcv_address1=rcv_address1, rcv_address2=rcv_address2, rcv_address3=rcv_address3,
                             rcv_extra_address=rcv_extra_address, rcv_date=rcv_date, user_email=user_email,
                             phone_type=phone_type)

    sim_order.order_state = 0
    if current_user is not None:
        sim_order.user_id = current_user.id

    db.session.add(sim_order)
    db.session.commit()
    return sim_order


def activation_simcard(first_name, last_name, phone_type, sim_number, sim_type, passport_img):
    """
    sim 활성화
    """
    product_sim = WirelessSimcardProduct.query.filter_by(sim_number=sim_number).first()
    sim_active = WirelessSimActivateModel(first_name=first_name, last_name=last_name, phone_type=phone_type,
                                     sim_type=sim_type, sim_number=sim_number, passport_img=passport_img)
    try:
        if product_sim is not None:
            product_sim.activate()

        db.session.add(sim_active)
        db.session.commit()
        return sim_active

    except:
        db.session.rollback()
        return None







def payment_simcard(sim_order_id):
    """

    :param sim_order_id: SimcardOrder instance
    :param user_id:
    :return:
    """
    sim_order = SimcardOrder.query.get(id=sim_order_id)

    if sim_order.user_id != current_user.id:
        return None

    try:
        # order_state 가 항상 0이어야 합니다.
        # order state 변경
        if sim_order.order_state == 0:
            sim_order.order_state = 1
            # payment 함수
            sim_payment = SimcardPayment()
            # payment = Payment~~
            sim_order.payment = sim_payment
        else:
            raise ValueError("주문 완료 되어 있어야 합니다.")
    except Exception as e:
        db.session.rollback()
        return None

    db.session.commit()

    return sim_order


def shipping_simcard(sim_order_id, sim_number):
    """

    :param sim_order_id:
    :param sim_number: Integer
    :return:
    """
    sim_order = SimcardOrder.query.get(id=sim_order_id)

    sim_order.sim_number = sim_number

    try:
        # order_state 가 항상 0이어야 합니다.
        # order state 변경
        if sim_order.order_state == 1:
            sim_order.order_state = 2
        else:
            raise ValueError("결제가  되어 있어야 합니다.")
    except Exception as e:
        db.session.rollback()
        return None

    db.session.commit()


def shipping_sim_confirm(sim_order_id):
    sim_order = SimcardOrder.query.get(id=sim_order_id)

    try:
        if sim_order.order_state == 2:
            sim_order.order_state = 3
        else:
            raise ValueError("배송 상태가  되어 있어야 합니다.")
    except Exception as e:
        db.session.rollback()
        return None

    db.session.commit()


def register_reserve_sim(sim_number):
    sim_order = SimcardOrder.query.filter_by(sim_number=sim_number).first()
    if sim_order is None:
        return None
    else:
        if sim_order.order_state == 3:
            sim_order.order_state = 4
        elif sim_order.order_state == 2:
            sim_order.order_state = 4
        else:
            db.session.rollback()
            raise ValueError("배송을 하지 않았습니다.")
        db.session.commit()

    return sim_order


def register_confirm_sim(sim_number):
    sim_order = SimcardOrder.query.filter_by(sim_number=sim_number).first()
    if sim_order is None:
        return None
    else:
        if sim_order.order_state == 4:
            sim_order.order_state = 5
        else:
            db.session.rollback()
            raise ValueError("등록 신청이 되지 않았습니다.")
        db.session.commit()
    return sim_order


def refund_sim(sim_order_id):
    sim_order = SimcardOrder.query.get(id=sim_order_id)
    if sim_order is None:
        return None
    else:
        if sim_order.order_state == 3:
            sim_order.order_state = 6
        else:
            db.session.rollback()
            raise ValueError("등록 신청이 되지 않았습니다.")
        db.session.commit()

    return sim_order



    #
    #
    # class SimcardPayment(BaseModel):
    #     """
    #     결제를 모아놓은 테이블
    #     """
    #     __tablename__ = 'wireless_sim_payment'
    #
    #     payment_method = db.Column(db.CHAR(6))
    #     amount = db.Column(db.DECIMAL(2))
    #
    #     def __repr__(self):
    #         return "<Sim Payment %r %r>" % (self.payment_method, self.amount)
    #
    # rcv_country = db.Column(db.String(2), db.ForeignKey('address_country.iso_3166_1_a2'))
    # rcv_address1 = db.Column(db.String(255))
    # rcv_address2 = db.Column(db.String(255))
    # rcv_address3 = db.Column(db.String(255))
    #
    # # 심 고유 번호
    # sim_number = db.Column(db.String(20))
    # # state
    #
    # user_name = db.Column(db.String(100))
    #
    # """
    # 0: 주문 완료
    # 1: 결제 완료
    # 2: 배송 준비
    # 3: 배송 완료
    # 4: 개통 완료
    # 5: 환불 신청
    # 6: 환불 완료
    # """
    # order_state = db.Column(db.Integer, default=0)
    # # 개통 폰번호
    # registered_phone = db.Column(db.String(12), nullable=True)
    #
    # # 개통일시
    # registered_date = db.Column(db.DateTime, nullable=True)
    #
    # # 여권 이미지
    # passport_img = db.Column(db.String(255), nullable=True)
    #
    # user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), index=True)
    # user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('sim_order', lazy='dynamic'))
    #
    # # 결제에 대한 관계키 설정
    # payment_id = db.Column(db.Integer, db.ForeignKey('wireless_sim_payment.id'))
    # payment = db.relationship('SimcardPayment', backref=db.backref('sim_order', lazy='dynamic'),
    #                           foreign_keys=[payment_id])
    #
    # @hybrid_property
    # def get_payment(self):
    #     if not self.payment:
    #         return None
    #     else:
    #         return self.payment
    #
    # def get_state(self):
    #     state = self.order_state
    #     if state == 0:
    #         return _("Ordered OK")
    #     elif state == 1:
    #         return _("Payment OK")
    #     elif state == 2:
    #         return _("Shipping Ready")
    #     elif state == 3:
    #         return _("Shipping OK")
    #     elif state == 4:
    #         return _("Register OK")
    #     elif state == 5:
    #         return _("Refund Ready")
    #     elif state == 6:
    #         return _("Refund OK")
    #
    # def __repr__(self):
    #     return "<SimcardOrder %r>" % self.sim_number
