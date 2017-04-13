import datetime
import os

from flask import render_template, redirect, request, url_for, session, abort, current_app, jsonify, flash
from flask.views import MethodView
from flask_security import login_required, current_user
from sqlalchemy import or_
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from flask_mail import Message
from apps.extensions import mail


from apps import db, app
from apps.api_server import trans_currency
from apps.api_server.payment.models import Payment
from apps.api_server.services.wireless_service.models import WirelessSimOrder, WirelessSimActivateModel, \
    WirelessRechargeModel
from apps.api_server.session_manager.checkout_session import WirelessCheckoutSessionData
from apps.utils.file_manager import upload_s3_mediafile
from apps.utils.payment import paypal
from apps.utils.payment.paypal import execute_payment
from .forms import WirelessOrderForm, WirelessActivationForm
from . import wireless_blueprint
from flask_babel import lazy_gettext as _


# 'Choose your plan -> Order SIM - > SIM Delivery -> Activation & Recharge'

class WirelessPlanView(MethodView):
    """
    요금제를 보여준다
    """
    location = (0, 'Choose your plan')

    def __init__(self):
        super().__init__()

    def get(self):
        return render_template('wireless/wireless_plan.html', location=self.location)

    def post(self):
        pass


class WirelessOrderView(MethodView):
    """
    선택한 요금제를 신청받고 결제를 준비한다.

    """
    plan_list = ['297plan', '585plan', 'payg']
    location = (1, 'Order Sim')
    sim_price = ('KRW', '11000')

    def __init__(self):

        super().__init__()

    # def pre_check_plan_name(self, plan_name):
    #     if plan_name not in self.plan_list:
    #         return abort(404)
    @login_required
    def get(self, plan_name=None):
        # self.pre_check_plan_name(plan_name)

        wireless_order_form = WirelessOrderForm()
        return render_template('wireless/wireless_order.html', form=wireless_order_form, location=self.location)

    @login_required
    def post(self, plan_name=None):
        # self.pre_check_plan_name(plan_name)

        wireless_order_form = WirelessOrderForm(request.form)

        if wireless_order_form.validate_on_submit():
            data = wireless_order_form.data

            if current_user.is_authenticated:
                user = current_user
            else:
                user = None

            # 모델에 추가
            wireless_order = WirelessSimOrder.make_first_order(data, user=user,
                                                               payment_method=data['payment_method'])

            if data['payment_method'] == 'paypal':
                currency, sim_price = trans_currency(self.sim_price[1], 'KRW', 'USD')

                # paypla item set
                sim_item = dict(
                    name='%s Sim Card, %s' % (plan_name, data['phone_type']),
                    price=sim_price,
                    currency=currency,
                    sku='%s' % plan_name,
                    quantity=1
                )

                order_number = wireless_order.order_number

                # session setting
                wireless_session = WirelessCheckoutSessionData()
                wireless_session.set_wireless_product('sim', sim_item['name'], order_number, 'paypal', currency,
                                                      sim_price, data['contact_no'], data['email'])

                details = dict(subtotal=sim_price, shipping='0')

                shipping_address = dict(
                    recipient_name=data['first_name'] + data['last_name'],
                    country_code='KR',
                    state=data['state'],
                    city=data['city'],
                    line1=data['line1'],
                    line2=data['line2'],
                )

                payer_info = {
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name']
                }

                # create payment
                payment = paypal.create_payment([sim_item], intent='sale', payer='', amount=sim_price, details=details,
                                                shipping_address=shipping_address, payer_info=payer_info,
                                                return_url='wireless/payment/execute/order',
                                                cancel_url='wireless/payment/cancel')

                for link in payment.links:
                    if link.method == "REDIRECT":
                        redirect_url = str(link.href)
                        return redirect(redirect_url)

        return render_template('wireless/wireless_order.html', form=wireless_order_form, location=self.location)


class WirelessPaymentExecuteView(MethodView):
    """
    승인받은 결제를 실행한다.
    """

    def __init__(self):
        self.wireless_session = WirelessCheckoutSessionData()
        super().__init__()
    @login_required
    def get(self, pay_loc):
        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')

        if payment_id is None or payer_id is None:
            return abort(404)

        if pay_loc == 'order':
            order_number = self.wireless_session._get('payment_data', 'order_number')

            order = WirelessSimOrder.get_with_order_number(order_number)

            # 결제 실행
            payment = execute_payment(payment_id, payer_id)
            payment_model = Payment(payment_method=order.payment_method, payment_unique_id=payment_id,
                                    currency=order.currency,
                                    paid_in_total=order.price)

            # 주문의 결제 상황 변경
            order.payment_complete()

            db.session.add(payment_model)
            order.payment = payment_model

            db.session.commit()
            return redirect(url_for('wireless.wireless_order_complete', order_number=order_number))

        elif pay_loc == 'recharge':
            recharge_order_number = self.wireless_session._get('payment_data', 'order_number')
            recharge = WirelessRechargeModel.get_with_order_number(recharge_order_number)

            payment = execute_payment(payment_id, payer_id)
            payment_model = Payment(payment_method=recharge.payment_method, payment_unique_id=payment_id,
                                    currency=recharge.currency, paid_in_total=recharge.price)

            recharge.payment_complete()

            db.session.add(payment_model)
            recharge.payment = payment_model
            db.session.commit()

            return redirect(url_for('wireless.wireless_order_complete', order_number=recharge_order_number))

    @login_required
    def post(self):
        pass


class WirelessPaymentCancelView(MethodView):
    """
    결제 중간 실패하였을때.
    """

    def get(self):
        return "취소"

    pass


class WirelessOrderComplete(MethodView):
    """
    결제가 완료되었을때 실행한다
    """

    @login_required
    def get(self):
        print("여기로 오나 ?")

        wireless_session = WirelessCheckoutSessionData()
        payment_data = wireless_session.get_namespace_dict('payment_data')
        wireless_session._flush_namespace('payment_data')
        print("payment data == ")
        print(payment_data)

        if payment_data['email']:

            msg = Message(subject='Wireless Order', html="<div class='space'>"
                                                         "<h3>Thank you for using KAMPERKOREA</h3>"
                                                         "<br/>"
                                                         "SIM order has been completed.<br/>"
                                                         "We will ship your item as soon as possible.<Br/>"
                                                         "When you have received the SIM please activate"
                                                         " it from our website.<Br/>"
                                                         "wwww.kamper.co.kr"
                                                         "<br/> Thank you.<Br/>"
                                                         "</div>",
                          recipients=[payment_data['email']])

            mail.send(msg)
            return render_template('wireless/wireless_order_complete.html', order_number=payment_data.get('order_number'),
                                   order_product_list=[payment_data['name']], payment_method=payment_data['method'],
                                   phone=payment_data['phone'], email=payment_data['email'])

        else:
            msg = Message(subject='Recharge Completed', html="<div class='space'>"
                                                             "<h3>Thank you for using KAMPERKOREA</h3>"
                                                             "<br/>"
                                                             "Your credit is now topped up.<br/>"
                                                             "If you have any questions please do not<Br/>"
                                                             "hesitate to email us or visit our website."
                                                             "<br/>www.kamper.co.kr<br/>"
                                                             "<br/> Thank you.<Br/>"
                                                             "</div>",
                          recipients=[current_user.email])

            mail.send(msg)

            return render_template('wireless/wireless_order_complete.html', order_number=payment_data.get('order_number'),
                                   order_product_list=[payment_data['name']], payment_method=payment_data['method'],
                                   phone=payment_data['phone'], email=current_user.email)


class WirelessActivation(MethodView):
    """
    휴대폰을 activation 하는 곳
    """
    _template_name = 'wireless/wireless_activate.html'

    _today = datetime.date.today()

    _upload_folder = 'wireless/passport'
    _upload_file_date = _today.strftime("%Y/%m/%d")
    _upload_prefix = os.path.join(_upload_folder, _upload_file_date)

    @login_required
    def get(self):
        form = WirelessActivationForm()
        return render_template(self._template_name, form=form)

    @login_required
    def post(self):
        form = WirelessActivationForm(CombinedMultiDict((request.files, request.form)))
        # PhotoForm(CombinedMultiDict((request.files, request.form)))
        # form = WirelessActivationForm(request.form)
        if form.validate_on_submit():
            data = form.data

            filename = 'passport_%s_%s' % (data['usim_number'], data['passport'].filename)
            passport_filename = secure_filename(filename)

            passport_filepath = os.path.join(self._upload_prefix, passport_filename)

            saved_filepath = upload_s3_mediafile(data['passport'], passport_filepath)
            print(saved_filepath)

            activate = WirelessSimActivateModel.first_activation_inquiry(
                english_name=data['english_name'], id_number=data['id_number'], birthday=data['birthday'],
                contact_no=data['contact_no'], address=data['address'], nationality_3166=data['nationality'],
                call_plan=data['call_plan'], phone_model=data['phone_model'], imei=data['imei'],
                sim_number=data['usim_number'], passport_img=saved_filepath, user=current_user
            )

            print(activate)
            db.session.add(activate)

            db.session.commit()
            return redirect(url_for('web_common.mypage_wireless'))

        return render_template(self._template_name, form=form)


class WirelessRecharge(MethodView):
    """
    휴대폰을 충전하는 곳
    """

    @login_required
    def get(self):
        user = current_user

        my_activate_list = user.activated_sim.filter(
            or_(WirelessSimActivateModel.status == WirelessSimActivateModel.STATE['ACTIVATION'],
                WirelessSimActivateModel.status == WirelessSimActivateModel.STATE['ORDER'],
                WirelessSimActivateModel.status == WirelessSimActivateModel.STATE['CANNOT'])
        ).first()

        # sim_activate_list = user.activated_sim.all()
        # sim_activate_list = user.activated_sim.filter_by(status=WirelessSimActivateModel.STATE['ACTIVATION']).all()

        return render_template('wireless/recharge.html', my_activate_list=my_activate_list)

    @login_required
    def post(self):
        user = current_user
        if not user.is_authenticated:
            return abort(404)

        activate_id = request.form.get('activate_id', None)
        recharge_quantity = int(request.form.get('recharge_quantity', 0))

        if (activate_id is None) or (not recharge_quantity > 0):
            return abort(401)

        activate_sim = user.activated_sim.filter_by(id=activate_id).first()

        if not activate_sim.status == WirelessSimActivateModel.STATE['ACTIVATION']:
            flash(_('It has not been activated yet.'))

            return render_template('wireless/recharge.html', my_activation_list=activate_sim)

        recharge_price = activate_sim.get_price_unit
        currency, price = trans_currency(recharge_price)

        payment_method = request.form.get('payment_method', None)

        price_amount = price * recharge_quantity

        recharge_order = WirelessRechargeModel.make_recharge_order(activate_sim, recharge_price, recharge_quantity,
                                                                   'KRW', user, payment_method)
        db.session.add(recharge_order)
        db.session.commit()

        item_name = '%s Recharge x%d' % (activate_sim.get_plan_type, recharge_quantity),

        wireless_session = WirelessCheckoutSessionData()
        wireless_session.set_wireless_product('recharge', item_name, recharge_order.order_number, 'paypal', currency,
                                              price_amount)
        if payment_method == 'paypal':

            recharge_item = dict(
                name='%s Recharge x%d' % (activate_sim.get_plan_type, recharge_quantity),
                price=price,
                currency=currency,
                sku='%s' % activate_sim.get_plan_type,
                quantity=recharge_quantity
            )
            details = dict(subtotal=price_amount, shipping='0')

            payment = paypal.create_payment([recharge_item], intent='sale', payer='', amount=price_amount,
                                            details=details,
                                            return_url='wireless/payment/execute/recharge',
                                            cancel_url='wirless/payment/cancel')

            print('충전이 안료 된다면 여가로 오나 ?')


            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_url = str(link.href)
                    return redirect(redirect_url)

        return render_template('wireless/recharge.html', my_activate_list=activate_sim)


wireless_blueprint.add_url_rule('/plan', view_func=WirelessPlanView.as_view('plan'))
wireless_blueprint.add_url_rule('/payment/execute/<pay_loc>',
                                view_func=WirelessPaymentExecuteView.as_view('payment_execute'))
wireless_blueprint.add_url_rule('/order', view_func=WirelessOrderView.as_view('order'))
wireless_blueprint.add_url_rule('/payment/cancel', view_func=WirelessPaymentCancelView.as_view('payment_cancel'))
wireless_blueprint.add_url_rule('/order/complete', view_func=WirelessOrderComplete.as_view('wireless_order_complete'))
wireless_blueprint.add_url_rule('/activation', view_func=WirelessActivation.as_view('activation'))
wireless_blueprint.add_url_rule('/recharge', view_func=WirelessRecharge.as_view('recharge'))



# 임시 파일 <ajax로 recharge 처리할때 쓰임>
@wireless_blueprint.route('/recharge_option', endpoint='get_recharge_info')
@login_required
def get_activate_recharge_format():
    activate_id = request.args.get('id')
    activate_sim = current_user.activated_sim.filter_by(id=activate_id,
                                                        status=WirelessSimActivateModel.STATE['ACTIVATION']).first()

    """
        전달 해줄 것
        form을 받으면 검색할 수 있나?
        1. pay as you go면 금액은 설정 가능
        2. 정액 요금제면 금액은 정해져 있다. (개월수만 설정 가능)
    """
    print(activate_sim)
    if not activate_sim:
        return jsonify(state=False, message=_('Not yet available. Please wait until activation.'))
    else:
        return jsonify(state=True, price_unit=activate_sim.get_price_unit, plan_type=activate_sim.get_plan_type)

#
# # prepaid_simcard order 및 장바구니 가능
# @wireless_blueprint.route('/')
# @wireless_blueprint.route('/simcard')
# def simcard():
#     return render_template('wireless/simcard.html')
#
#
# @wireless_blueprint.route('/simcard/list')
# def simcard_list():
#     return render_template('wireless/simcard_list.html')
#
#
# @wireless_blueprint.route('/simcard/request', methods=('GET', 'POST'))
# # @login_required
# def simcard_request():
#     if request.method == 'POST':
#         # 보류
#         sim_type = request.form.get('sim_type')
#         if sim_type is None:
#             sim_type = '4G'
#
#         return redirect(url_for('wireless.simcard_order'))
#     return render_template('wireless/simcard_request.html')
#
#
#
# @wireless_blueprint.route('/simcard/inquiry')
# def simcard_inquiry():
#     return render_template('wireless/simcard_inquiry.html')
#


@wireless_blueprint.route('/main')
def wireless_main():
    return render_template('wireless/main.html')