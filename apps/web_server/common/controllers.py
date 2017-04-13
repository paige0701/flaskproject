from decimal import Decimal

import datetime


from flask import request, render_template, redirect, session, current_app, url_for, after_this_request, abort, flash
from flask_babel import lazy_gettext as _
from flask_security.changeable import change_user_password

from flask_security import auth_token_required, http_auth_required, login_required, current_user, auth_required
from flask_security.views import _commit
from flask_security.forms import ChangePasswordForm

from flask_mail import Message
from flask_wtf import Form

from apps.api_server.auth.form import ProfileFirstNameForm, ProfileLastNameForm, ProfileNumberForm
from apps.api_server.auth.utils import updatefirstname, updatelastname, updatenumber

from apps.extensions import mail

from sqlalchemy import desc, extract
from wtforms import StringField, FileField

from apps import db
from apps.api_server.payment.form import CheckoutForm

from apps.api_server.payment.models import Order, OrderLineItem, ProductReturn
from apps.api_server.payment.utils import make_order, make_payment, make_order_association, update_order_line
from apps.api_server.services.catalogue_service.form import ProductRefundForm

from apps.api_server.services.catalogue_service.models import CatalogueProductCart, CatalogueProduct, CatalogueLineItem
from apps.api_server.services.catalogue_service.utils import makeProductReturn
from apps.utils.file_manager import upload_s3_mediafile
from apps.web_server.common import common_blueprint
from apps.utils.payment.paypal import create_payment, execute_payment
from apps.api_server.address.models import UserAddress


@common_blueprint.route('/')
def index():
    return render_template("common/index.html")


class TempForm(Form):
    string = StringField('name')
    file = FileField('files')


@common_blueprint.route('/test1212', methods=['POST', 'GET'])
def test_index():
    form = TempForm()
    if request.method == 'POST':
        form = TempForm(request.form)
        if form.validate():
            print("validate")
            print(form)
            print('--------!!!!!!!!')
            file = request.files['file']
            print(file)
            print('--------!!!!!!!!')
            print(file.filename)
            print(file)
            upload_s3_mediafile(file, 'pp/dk.jpg')


from apps.api_server.session_manager.checkout_session import CheckoutSessionData


# @common_blueprint.route('/')
# def index():
#     return render_template("common/index.html")
#
#
#     return render_template('temp.html', form=form)


@common_blueprint.route('/after_login')
@login_required
def temp_index3():
    print(current_user.get_auth_token())
    print(current_user)
    print(request)

    for x in request.environ:
        print(x)
        if x is 'Authentication-Token':
            print("Authentication=token = %s" % str(request.environ[x]))
    return "login_required"


@common_blueprint.route('/auth')
@auth_required('basic', 'token', 'session')
def temp_index4():
    return "auth_required"


@common_blueprint.route('/temp12')
def temp12():
    return render_template('base.html')


# 여기서 부터는 footer
@common_blueprint.route('/aboutkamper')
def aboutkamper():
    return render_template('partials/aboutkamper.html')


@common_blueprint.route('/teamkamper')
def teamkamper():
    return render_template('partials/teamkamper.html')


@common_blueprint.route('/useragreement')
def useragreement():
    return render_template('partials/useragreement.html')


@common_blueprint.route('/privacypolicy')
def privacypolicy():
    return render_template('partials/privacypolicy.html')


@common_blueprint.route('/privacypolicy_kr')
def privacypolicy_kr():
    return render_template('partials/privacypolicy_kr.html')


@common_blueprint.route('/useragreement_kr')
def useragreement_kr():
    return render_template('partials/useragreement_kr.html')


# 웹사이트 상단에 My Page - My Order 라는 메뉴를 눌렀을 때
@common_blueprint.route('/my_orders')
@login_required
def my_orders():
    userid = current_user.id
    current_month = str(datetime.date.today().strftime("%m"))
    current_year = (datetime.date.today().strftime("%Y"))
    current = current_year + '-' + current_month
    order = Order.query.filter(Order.user_id == userid) \
        .filter(extract('year', Order.created_at) == current_year) \
        .filter(extract('month', Order.created_at) == current_month).order_by(desc(Order.created_at)).all()

    # order = OrderLineItem.query.filter(OrderLineItem.order_relation.user_id == userid) \
    #     .filter(extract('year', Order.created_at) == current_year) \
    #     .filter(extract('month', Order.created_at) == current_month).order_by(desc(Order.created_at)).all()

    # for x in order:
    #     order = OrderLineItem.query.filter(OrderLineItem.order_id==x.id).all()
    print("이거 필요해 ....", order)

    for x in order:
        ll = x.order_line.all()
        # ll  = OrderLineItem.query.filter(OrderLineItem.order_id==x.id).all()
        print("how ar ", ll)

    return render_template('common/my_orders.html', order=order, current=current)


# 웹사이트 상단에 My Page - My Wireless 라는 메뉴를 눌렀을 때
@common_blueprint.route('/mypage/wireless')
@login_required
def mypage_wireless():

    if not current_user.is_authenticated:
        return abort(401)

    user = current_user




    sim_order_list = user.sim_order.all()
    sim_activate_list = user.activated_sim.all()
    sim_recharge_list = user.sim_recharge.all()
    for x in sim_recharge_list:
        print(x.id)

    return render_template('common/mypage/wireless.html', sim_order_list=sim_order_list, sim_activate_list=sim_activate_list, sim_recharge_list=sim_recharge_list)


# 웹사이트 상단에 My Page - My Returns 라는 메뉴를 눌렀을 때
@common_blueprint.route('/my_returns')
@login_required
def my_returns():
    user_id = current_user.id

    product = db.session.query(ProductReturn, OrderLineItem).filter(
            ProductReturn.product_id == OrderLineItem.product_id). \
        filter(ProductReturn.order_id == OrderLineItem.order_id).filter(OrderLineItem.user_id == user_id).all()

    current_month = str(datetime.date.today().strftime("%m"))
    current_year = (datetime.date.today().strftime("%Y"))
    current = current_year + '-' + current_month

    return render_template('common/my_returns.html', product=product, current=current)


# order 확인 하는 페이지에서 날짜를 바꿨을 때
@common_blueprint.route('/date_changed')
def date_changed():
    print("여기로오냥~~~~~~~~~~~~")
    datee = request.args.get("usr")
    if datee:
        t = datee.split('-')
        datee = []
        for x in t:
            datee.append(x)
        print(datee)

        current = datee[0] + '-' + datee[1]
        userid = current_user.id
        # current_month = str(datetime.date.today().strftime("%m"))
        # current_year = (datetime.date.today().strftime("%Y"))
        order = Order.query.filter(Order.user_id == userid) \
            .filter(extract('year', Order.created_at) == datee[0]) \
            .filter(extract('month', Order.created_at) == datee[1]).order_by(desc(Order.created_at)).all()
        return render_template('common/my_orders.html', order=order, current=current)


# 반품 신청
@common_blueprint.route('/product_return/<int:order>/<int:product_id>')
@login_required
def product_return(order, product_id):
    print("order_id = ", order)
    print("product_id =", product_id)
    refundfrm = ProductRefundForm()
    session['return_order_id'] = order
    session['return_product_id'] = product_id

    return render_template('common/product_return.html', form=refundfrm)


# 반품 신청 완료
@common_blueprint.route('/product_return_complete', methods=['POST'])
@login_required
def product_return_complete():
    refundfrm = ProductRefundForm(request.form)
    formData = refundfrm.data

    if refundfrm.validate():

        order_id = session['return_order_id']
        product_id = session['return_product_id']
        exchange_refund = formData['exchange_refund']
        refund_reason = formData['refund_reason']
        quantity = formData['quantity']
        email = formData['email']
        contact_number = formData['contact_number']
        message = formData['message']

        productReturn = makeProductReturn(email, quantity, product_id, order_id, contact_number, message, refund_reason,
                                          exchange_refund)

        if productReturn is None:
            return None
        else:
            db.session.add(productReturn)
            db.session.commit()

            # 2. item_line 에 status 를 바꾼다
            updatee = update_order_line(order_id, product_id)

        # 1. ProductReturn table 에 인서트 한다
        # product_id, order_id, quantity, exchange_refund 여부, 반납이유, status 인서트 한다
        # 완료 되면 email 을 confirmation 으로 보내고 다음 스텝을 진행 할 수 있는 이메일을 포함해서 보낸다
        # status 가 바뀌면 email 을 통해 연락한다

        whichone = productReturn.get_exchangeORrefund
        returnid = productReturn.get_productReturnId
        msg = Message(subject='Return Request', html="<div class='space'>"
                                                     "<h3>Thank you for using KAMPERKOREA</h3>"
                                                     "<br/>"
                                                     + whichone +
                                                     " has been requested.<br/>"
                                                     "Please check your e-mail regularly for updates.<br/><br/>"
                                                     "Sorry for the inconvenience.<br/><br/>"
                                                     "wwww.kamper.co.kr"
                                                     "</div>",
                      recipients=[email])

        mail.send(msg)

        return render_template('common/product_return_complete.html', email=email, whichone=whichone, returnid=returnid)

    else:
        return render_template('common/product_return.html', form=refundfrm)


# --------------------------------------------------- 결제 부분 ----------------------------------------------------------

# 바로 결제 1
@common_blueprint.route('/buy_now/<int:no>', methods=['GET', 'POST'])
@login_required
def buy_now(no):
    print(request.method)
    product = CatalogueProduct.query.filter(CatalogueProduct.id == no).first()
    quantity = request.form['quantity']

    print("when buy now button in presses from product_detail.html")

    checkout_session = CheckoutSessionData()
    checkout_session.set_order_method('direct')
    product_list = [{'product_id': product.id, 'quantity': quantity}]
    checkout_session.set_product_list(product_list)

    return redirect('product_buynow_checkout')


# 바로 결제 2
@common_blueprint.route("/product_buynow_checkout", methods=['POST', 'GET'])
@login_required
def product_buynow_checkout():
    chkform = CheckoutForm()

    userid = current_user.id

    checkout_session = CheckoutSessionData()

    prod = checkout_session.get_product_list()

    for prod in prod:
        quantity = prod.get('quantity', None)
        product_id = prod.get('product_id', None)
        if quantity is None or product_id is None:
            return redirect(request.referrer)

    address = UserAddress.query.filter(UserAddress.user_id == userid).first()
    product = CatalogueProduct.query.filter(CatalogueProduct.id == product_id).first()

    total = int(product.price) * int(quantity)

    if total < 30000:
        shipping = 3000
    else:
        shipping = 0
    total_amount = total + shipping

    if request.method == 'POST':
        print("when checkout button is pressed from checkout.html")
        chkform = CheckoutForm(request.form)
        if chkform.validate():
            checkout_session = CheckoutSessionData()

            checkout_session.set_payment_method(method='PayPal')
            checkout_session.set_email(request.form['email'])
            payer_info = {
                'email': request.form['email'], 'first_name': request.form['firstname'],
                'last_name': request.form['lastname']
            }

            shipping_data = chkform.data
            shipping_data['postal_code'] = '12345'
            firstname = shipping_data['firstname']
            lastname = shipping_data['lastname']
            recipient_name = firstname + ' ' + lastname
            shipping_data.pop('firstname')
            shipping_data.pop('lastname')
            shipping_data['recipient_name'] = recipient_name
            shipping_data.pop('comments')
            shipping_data.pop('email')

            # billing_address = {'country_code': address.iso_3166_country, 'state': address.province,
            #                    'city': address.address1, 'line1': address.address2,
            #                    'line2': address.address3, 'phone': address.phone
            #                    }

            # checkout_session.set_shipping_address(shipping_data)
            # checkout_session.set_billing_address(billing_address)

            product_list = []

            amount_price = round(0, 2)

            # for prod in _product_list:
            #     quantity = prod.get('quantity', None)
            #     product_id = prod.get('product_id', None)
            #     if quantity is None or product_id is None:
            #         return redirect(request.referrer)

            prd = CatalogueProduct.query.filter_by(id=product_id).first()

            amount_price += Decimal(quantity) * prd.get_usd_price
            subtotal = amount_price
            product_list.append(dict(
                    name=prd.get_title,
                    price=str(prd.get_usd_price),
                    currency='USD',
                    sku=prd.upc,
                    quantity=quantity))

            if amount_price < 27.30:
                shipping = 2.72
            else:
                shipping = 0.0

            amount_price = round(Decimal(subtotal), 2) + round(Decimal(shipping), 2)

            amount_price = str(round(amount_price, 2))
            details = dict(subtotal=str(subtotal), shipping=str(shipping))

            payment = create_payment(product_list, "sale", current_user.id, "hi", "hi", amount_price, details,
                                     shipping_data, payer_info)

            print('----')
            print(payment)

            for link in payment.links:
                if link.method == "REDIRECT":
                    # Convert to str to avoid google appengine unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    redirect_url = str(link.href)
                    print("Redirect for approval: %s" % (redirect_url))

                    return redirect(redirect_url)

    total = "{:,}".format(total)
    total_amount = "{:,}".format(total_amount)
    shipping = "{:,}".format(shipping)

    return render_template('common/checkout.html', chkform=chkform, product=product, quantity=quantity,
                           total=total, shipping=shipping, total_amount=total_amount, address=address)


# 카트결제 1
@common_blueprint.route('/product_cart_checkout', methods=['POST', 'GET'])
def product_cart_checkout():
    print("카트에서 결제를 누른후 checkout 버튼을 누르면 이쪽으로 온다")
    checkout_session = CheckoutSessionData()
    checkout_session.set_order_method('cart')
    userid = current_user.id
    cart = CatalogueProductCart.query.filter(CatalogueProductCart.user_id == userid).first()
    address = UserAddress.query.filter(UserAddress.user_id == userid).first()
    chkform = CheckoutForm(request.form)

    if request.method == 'POST':
        print("when checkout button is pressed from checkout.html")
        if chkform.validate():

            checkout_session.set_payment_method(method='PayPal')
            checkout_session.set_email(request.form['email'])

            payer_info = {
                'email': request.form['email'], 'first_name': request.form['firstname'],
                'last_name': request.form['lastname']
            }
            print('p_info:', payer_info)
            # print(chkform)
            # shipping_address = {'country_code': chkform['country_code'], 'state': chkform['state'],
            #                     'city': chkform['city'], 'line1': chkform['line1'],
            #                     'line2': chkform['line2'], 'phone': chkform['phone'],
            #                     'postal_code': '12345', 'recipient_name': chkform['firstname']+' '+request.form['lastname']
            #                     }

            shipping_data = chkform.data
            shipping_data['postal_code'] = '12345'
            firstname = shipping_data['firstname']
            lastname = shipping_data['lastname']
            recipient_name = firstname + ' ' + lastname
            shipping_data.pop('firstname')
            shipping_data.pop('lastname')
            shipping_data['recipient_name'] = recipient_name
            shipping_data.pop('comments')
            shipping_data.pop('email')

            #
            # billing_address = {'country': 'KR', 'province': 'Seoul',
            #                    'address1': 'Seoul', 'address2': 'Gangnam-gu',
            #                    'address3': '45-98 205ho', 'phone': '01066681343'
            #                    }

            checkout_session.set_shipping_address(shipping_data)
            # checkout_session.set_billing_address(billing_address)

            line = CatalogueLineItem.query.filter(CatalogueLineItem.cart_id == cart.id).all()

            amount_price = round(0, 2)
            product_list = []
            p_list = []
            for x in line:
                p_list.append(dict(product_id=x.product.id, quantity=x.quantity))
                product_list.append(dict(
                        name=x.product.get_title,
                        price=str(x.product.get_usd_price),
                        currency='USD',
                        sku=x.product.upc,
                        quantity=x.quantity))
                amount_price += Decimal(x.quantity) * x.product.get_usd_price

            subtotal = amount_price

            if amount_price < 27.30:
                shipping = 2.72
            else:
                shipping = 0.0

            checkout_session.set_product_list(p_list)
            amount_price = round(Decimal(subtotal), 2) + round(Decimal(shipping), 2)
            amount_price = str(round(amount_price, 2))
            details = dict(subtotal=str(subtotal), shipping=str(shipping))

            payment = create_payment(product_list, "sale", current_user.id, "hi", "hi", amount_price, details,
                                     shipping_data, payer_info)

            for link in payment.links:
                if link.method == "REDIRECT":
                    # Convert to str to avoid google appengine unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    redirect_url = str(link.href)
                    print("Redirect for approval: %s" % (redirect_url))

                    return redirect(redirect_url)

    return render_template('common/checkout.html', chkform=chkform, cart=cart, address=address)


@common_blueprint.route('/execute', methods=['POST', 'GET'])
def product_execute():
    paymentid = request.args.get('paymentId')
    payerid = request.args.get('PayerID')

    payment = execute_payment(paymentid, payerid)
    payment_dict = payment.to_dict()

    currency = payment_dict.get('transactions', None)[0].get('amount').get('currency')
    total = payment_dict.get('transactions', None)[0].get('amount').get('total')
    subtotal = payment_dict.get('transactions', None)[0].get('amount').get('details').get('subtotal')
    shipping = payment_dict.get('transactions', None)[0].get('amount').get('details').get('shipping')

    # shipping_method = 'shipping'
    # order_state = payment_dict.get('state')
    user_email = payment_dict.get('payer').get('payer_info').get('email')
    name = payment_dict.get('payer').get('payer_info').get('shipping_address').get('recipient_name')
    payment_method = payment_dict.get('payer').get('payment_method')
    print(current_user)
    user_id = current_user.id
    # shipping_country = payment_dict.get('payer').get('payer_info').get('shipping_address').get('country_code')
    country_code = 'KR'
    shipping_state = payment_dict.get('payer').get('payer_info').get('shipping_address').get('state')
    shipping_city = payment_dict.get('payer').get('payer_info').get('shipping_address').get('city')
    shipping_line1 = payment_dict.get('payer').get('payer_info').get('shipping_address').get('line1')
    shipping_line2 = payment_dict.get('payer').get('payer_info').get('shipping_address').get('line2')
    payment_unique_id = payment_dict.get('id')
    order_state = 0

    order = make_order(currency, subtotal, shipping, total, user_email, name, order_state,
                       payment_method,
                       user_id, country_code, shipping_state, shipping_city, shipping_line1, shipping_line2)

    try:
        db.session.add(order)
        db.session.commit()

    except:
        current_app.logger.error('payment DB Insert failed \n Paymnet_id: %s' % paymentid)
        db.session.rollback()

    checkoutsession = CheckoutSessionData()
    ck = checkoutsession.get_product_list()
    print("ck ==  ", ck)
    for x in ck:
        order_association = make_order_association(x.get('product_id'), x['quantity'], order.id, order_state, user_id)
        try:
            db.session.add(order_association)
            db.session.commit()
        except:
            current_app.logger.error('order lineitem insert failed !!!!!! :( \n Paymnet_id: %s' % paymentid)
            db.session.rollback()

    pay = make_payment(order.id, payment_method, currency, total, payment_unique_id)
    checkoutsession.set_order_number(order.id)

    try:
        db.session.add(pay)
        db.session.commit()
    except:
        current_app.logger.error('payment DB Insert failed \n Paymnet_id: %s' % paymentid)
        db.session.rollback()

    method = checkoutsession.get_order_method()
    if method == 'cart':
        p_dict = []
        for x in ck:
            p_dict.append(str(x.get('product_id')))
        k = CatalogueProductCart.query.filter(CatalogueProductCart.user_id == user_id).first()
        k.remove_line_item(p_dict)
        db.session.commit()

    msg = Message(subject='Thank you for ordering', html="<div class='space'>"
                                                         "<h3>Thank you for using KAMPERKOREA</h3>"
                                                         "<br/>"
                                                         "Your order " + str(checkoutsession.get_order_number()) +
                                                         " has been completed.<br/>"
                                                         "You have made a payment with "
                                                         + str(payment_method) + ".<br/><br/>"
                                                                                 "Please check your order status at<br/><br/>"
                                                                                 "wwww.kamper.co.kr"
                                                                                 "</div>",
                  recipients=[user_email])
    mail.send(msg)

    return redirect(url_for('web_common.order_complete'))


# 주문 완료
@common_blueprint.route('/order/complete')
def order_complete():
    chk_session = CheckoutSessionData()
    email = chk_session.get_email()
    payment_method = chk_session.get_payment_method()
    # unique_id =chk_session.get_payment_unique_id()
    order_number = chk_session.get_order_number()
    return render_template('common/order_complete.html', email=email, payment_method=payment_method,
                           order_number=order_number)


# 마이페이지
@common_blueprint.route('/myPage')
@login_required
def auth_mypage():

    firstnameform = ProfileFirstNameForm()
    lastnameform = ProfileLastNameForm()
    numberform = ProfileNumberForm()
    passwordform = ChangePasswordForm()
    return render_template('common/mypage.html', firstnameform=firstnameform, lastnameform=lastnameform,
                           numberform=numberform, passwordform=passwordform)


# 마이페이지에서 이름 (first name) 을 수정한다
@common_blueprint.route('/firstName', methods=['POST'])
def changefirstname():
    if request.method == 'POST':

        firstnameform = ProfileFirstNameForm(request.form)
        lastnameform = ProfileLastNameForm(request.form)
        numberform = ProfileNumberForm(request.form)
        passwordform = ChangePasswordForm(request.form)

        if firstnameform.validate():
            firstname = firstnameform.data
            updatefirstname(current_user.id, firstname['firstname'])
            flash(_('Name changed'))

            return render_template('common/mypage.html', firstnameform=firstnameform, lastnameform=lastnameform,
                                   numberform=numberform, passwordform=passwordform)

        else:
            return render_template('common/mypage.html', firstnameform=firstnameform, lastnameform=lastnameform,
                                   numberform=numberform, passwordform=passwordform)


# 마이페이지에서 성 (last name) 을 수정한다
@common_blueprint.route('/lastName', methods=['POST'])
def changelastname():
    if request.method == 'POST':

        lastnameform = ProfileLastNameForm(request.form)
        firstnameform = ProfileFirstNameForm(request.form)
        numberform = ProfileNumberForm(request.form)
        passwordform = ChangePasswordForm(request.form)

        if lastnameform.validate():
            lastname = lastnameform.data
            updatelastname(current_user.id, lastname['lastname'])
            flash(_('Last name changed'))

            return render_template('common/mypage.html', lastnameform=lastnameform, firstnameform=firstnameform,
                                   numberform=numberform, passwordform=passwordform)

        else:
            return render_template('common/mypage.html', lastnameform=lastnameform, firstnameform=firstnameform,
                                   numberform=numberform, passwordform=passwordform)


# 마이페이지에서 전화번호 (contact number) 을 수정한다
@common_blueprint.route('/contactNumber', methods=['POST'])
def changecontactnumber():
    if request.method == 'POST':

        lastnameform = ProfileLastNameForm(request.form)
        firstnameform = ProfileFirstNameForm(request.form)
        numberform = ProfileNumberForm(request.form)
        passwordform = ChangePasswordForm(request.form)

        if numberform.validate():
            number = numberform.data
            updatenumber(current_user.id, number['contactnumber'])
            flash(_('Number changed'))

            return render_template('common/mypage.html', lastnameform=lastnameform, firstnameform=firstnameform,
                                   numberform=numberform, passwordform=passwordform)

        else:
            return render_template('common/mypage.html', lastnameform=lastnameform, firstnameform=firstnameform,
                                   numberform=numberform, passwordform=passwordform)


# 마이페이지에서 비밀번호 (password) 을 수정한다
@common_blueprint.route('/changepassword', methods=['POST'])
def changepassword():
    if request.method == 'POST':

        lastnameform = ProfileLastNameForm(request.form)
        firstnameform = ProfileFirstNameForm(request.form)
        numberform = ProfileNumberForm(request.form)

        passwordform = ChangePasswordForm(request.form)

        if passwordform.validate():
            print(passwordform.errors)
            after_this_request(_commit)
            change_user_password(current_user, passwordform.new_password.data)
            flash(_('Password changed'))
            return redirect(url_for('web_common.auth_mypage'))

        else:
            print(passwordform.errors)
            return render_template('common/mypage.html', lastnameform=lastnameform, firstnameform=firstnameform,
                                   numberform=numberform, passwordform=passwordform)
