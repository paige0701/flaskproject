import json
from apps import db
from apps.api_server.payment.models import Payment, OrderLineItem, Order, ProductReturn
from flask import request,redirect


def make_order(currency, amount, shipping, total_amount, user_email, name,order_state,
               payment_method, user_id,
               country_code, shipping_state, shipping_city, shipping_line1, shipping_line2):
    # billing_country=None, billing_state=None, billing_city=None, billing_line1=None, billing_line2=None, message=None):

    order = Order(currency=currency, subtotal=amount, shipping_fee=shipping, total=total_amount,
                  user_email=user_email,order_state=order_state,
                  name=name,payment_method=payment_method, user_id=user_id,
                  shipping_iso_3166_country=country_code,shipping_state=shipping_state,
                  shipping_city=shipping_city, shipping_line1=shipping_line1, shipping_line2=shipping_line2)
    # billing_state=billing_state, billing_city=billing_city, billing_line1=billing_line1,
    # billing_line2=billing_line2, billing_country=billing_country, )

    return order


def make_order_association(product_id, quantity, order_id,order_state,user_id):

    line_item = OrderLineItem(product_id=product_id,order_id=order_id,quantity=quantity,status=order_state,user_id=user_id)
    return line_item


def make_payment(order_id, payment_method, currency, total_amount_paid, payment_unique_id):

    payment = Payment(order_id=order_id, payment_method=payment_method, currency=currency,
                      paid_in_total=total_amount_paid,
                      payment_unique_id=payment_unique_id)

    return payment


def dictionary_to_json_exclude_null(_dict):
    # serialize dict to json exclude None
    return json.dumps(dict((k, v) for k, v in _dict.items() if v is not None))


# def create_with_paypal(items, shipping_charge):
#     amount_total = 0
#     for item in items:
#         amount_total += item.price
#     payment_dict = {
#         "intent": "sale",  # express checkout
#         # "experience_profile_id": web_profile,
#         "redirect_urls": redirect_urls,
#         "payer": {
#             "payment_method": "paypal",  # paypal
#             "payer_info": {
#                 #     billing_address
#
#             }
#         },
#         "transactions": [
#             {
#                 # ItemList
#                 "item_list": {
#                     "items": items,
#
#                     # "shipping_address": {
#                     #     "recipient_name": shipping_address.name,
#                     #     "line1": shipping_address.line1 + shipping_address.line2 + shipping_address.line3,
#                     #     "city": shipping_address.line4,
#                     #     "country_code": shipping_address.country.iso_3166_1_a2,
#                     #     "postal_code": shipping_address.postcode,
#                     #     "state": shipping_address.state
#                     # }
#
#                 },
#                 # Amount
#                 # Let's you specify a payment amount.
#                 "amount": {
#                     # "total": str(order_total.incl_tax),  # 금액
#                     "total": amount_total,  # 금액
#                     "currency": "USD",
#                     "details": {
#                         "subtotal": amount_total,
#                         "shipping": amount_total + shipping_charge,
#                     }
#                     # https://developer.paypal.com/docs/integration/direct/rest-api-payment-country-currency-support/
#                 },
#                 "description": "Thank you",
#             }
#         ]
#     }
#     payment = paypalrestsdk.Payment(dictionary_to_json_exclude_null(payment_dict))
#
#     # Create Payment and return status( True or False )
#     if payment.create():
#         print("Payment[%s] created successfully" % payment.id)
#     else:
#         print("Error while creating payment:")
#         print(payment.error)
#
#     return payment


# order_line status update  하기
def update_order_line(order_id,product_id):
    print("here")
    line = OrderLineItem.query.filter_by(product_id=product_id, order_id = order_id).first()
    print(line)
    line.status = 4
    db.session.add(line)
    db.session.commit()
    return line



