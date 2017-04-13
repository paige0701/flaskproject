import json

import paypalrestsdk
from flask import current_app, jsonify
from werkzeug.local import LocalProxy


_current_app = LocalProxy(lambda: current_app)

paypalrestsdk.configure({
    "mode": _current_app.config['PAYPAL_MODE'],
    "client_id": _current_app.config['PAYPAL_CLIENTID'],
    "client_secret": _current_app.config['PAYPAL_SECRET']})

redirect_urls = {
    "return_url": _current_app.config['PAYPAL_RETURN_URL'],
    "cancel_url": _current_app.config['PAYPAL_CANCEL_URL']
}


def create_payment(intent, payer, transactions, experience_profile_id, note_to_payer, redirect_urls=redirect_urls):
    """
    create payment - if you want to know more, Go there <https://developer.paypal.com/docs/api/payments/>
    :param intent: Required -
                    Payment intent. Must be set to sale for immediate payment,
                    authorize to authorize a payment for capture later,
                    or order to create an order.
    :param payer: Required -
                    Source of the funds for this payment represented by a PayPal account or a direct credit card.
    :param transactions: Required -
                    Transaction details, if updating a payment.
                    Note that this instance of the transactions object accepts only the amount object.
    :param experience_profile_id:
                    PayPal generated identifier for the merchant's payment experience profile.
                    Refer to this link to create experience profile ID.
    :param note_to_payer:
                    free-form field for the use of clients to pass in a message to the payer
    :param redirect_urls:
                    Set of redirect URLs you provide only for PayPal-based payments.

    :return:
    """

    if intent not in ['sale', 'authorize', 'order']:
        _current_app.logger.error("Value Error: payment's intent is always in ['sale','authorize','order']")
        raise ValueError



    paypalrestsdk.Payment({

        "redirect_urls": redirect_urls
    })

class RestObject(object):
    def to_json(self):
        return dictionary_to_json_exclude_null(self.__dict__)


def execute_payment():
    pass


def show_payment_detail(payment_id):
    pass


def update_payment(payment_id):
    pass


def list_payments(count, start_id, start_index, start_time):
    pass


class Paypal_Payment(RestObject):
    def __init__(self, intent, payer, transactions, experience_profile_id=None, note_to_payer=None, redirect_urls=None):
        if intent not in ['sale', 'authorize', 'order']:
            _current_app.logger.error("Value Error: payment's intent is always in ['sale','authorize','order']")
            raise ValueError

        self.intent = intent
        self.payer = payer
        self.transactions = transactions
        self.experience_profile_id = experience_profile_id
        self.note_to_payer = note_to_payer
        self.redirect_urls = redirect_urls


class Payer(RestObject):
    def __init__(self, payment_method, funding_instruments=None, external_selected_funding_instrument_type=None,
                 payer_info=None,
                 status=None):
        if payment_method not in ['paypal', 'credit_card']:
            # 한국에서는 credit_card 사용 제한
            # _current_app.logger.error("Value Error: payment method is always in ['paypal','credit_card']")
            raise ValueError

        self.payment_method = payment_method
        self.status = status
        self.funding_instruments = funding_instruments
        self.external_selected_funding_instrument_type = external_selected_funding_instrument_type
        self.payer_info = payer_info

    def get_json(self):
        return dictionary_to_json_exclude_null(self.__dict__)


class Transactions(RestObject):
    """
    For more Detail https://developer.paypal.com/docs/api/payments/#definition-transaction
    """

    def __init__(self, amount=None, payee=None, description=None, note_to_payee=None, custom=None, invoice_number=None,
                 soft_descriptor=None, payment_options=None, item_list=None, notify_url=None, order_url=None,
                 related_resource=None):
        """
        :param amount: <PaymentAmount()>
        :param payee: <Payee>
        :param description: <str>
        :param note_to_payee: <string>
        :param custom: <str> free-form field for the use of clients
        :param invoice_number: <str> invoice number to track this payment
        :param soft_descriptor: <str> Soft descriptor used when charging this funding source.
                                    If length exceeds max length, the value will be truncated
        :param payment_options: <enum> {'allowed_payment_method': ('UNRESTRICTED' OR 'INSTANT_FUNDING_SOURCE' OR 'IMMEDIATE_PAY' )}
        :param item_list:
        :param notify_url:
        :param order_url:
        :param related_resource:
        :return:
        """
        self.amount = amount
        self.payee = payee
        self.description = description
        self.note_to_payee = note_to_payee
        self.custom = custom
        self.invoice_number = invoice_number
        self.soft_descriptor = soft_descriptor
        self.payment_options = payment_options
        self.item_list = item_list
        self.notify_url = notify_url
        self.order_url = order_url
        self.related_resources = related_resource


class PaymentAmount(RestObject):
    def __init__(self, currency=None, total=None, details=None):
        """
        For more details: https://developer.paypal.com/docs/api/payments/#definition-payment_amount

        :param currency: <str> 3-letter currency code. PayPal does not support all currencies.
        :param total: <str> Total amount charged from the payer to the payee. In case of a refund, this is the refunded
                            amount to the original payer from the payee. 10 characters max with support for 2 decimal places.
        :param details: <AmountDetail> Additional details of the payment amount.
        :return:
        """
        self.currency = currency  # string
        self.total = total  # string
        self.details = details  # object


class AmountDetail(RestObject):
    """
    https://developer.paypal.com/docs/api/payments/#definition-details
    """

    def __init__(self, subtotal=None, shipping=None, tax=None, handling_fee=None, shipping_discount=None,
                 insurance=None, gift_wrap=None):
        """
        :param subtotal: <str> Amount of the subtotal of the items. Required if line items are specified. 10 characters max,
                            with support for 2 decimal places.
        :param shipping: <str> Amount charged for shipping. 10 characters max with support for 2 decimal places.
        :param tax: <str> Amount charged for tax. 10 characters max with support for 2 decimal places.
        :param handling_fee: <str> Amount being charged for the handling fee.
                                Only supported when the payment_method is set to paypal.
        :param shipping_discount: <str> Amount being discounted for the shipping fee.
                                Only supported when the payment_method is set to paypal.
        :param insurance: <str> Amount being charged for the insurance fee. Only supported when the payment_method is set to paypal.
        :param gift_wrap: <str> Amount being charged as gift wrap fee.
        """
        self.subtotal = subtotal
        self.shipping = shipping
        self.tax = tax
        self.handling_fee = handling_fee
        self.shipping_discount = shipping_discount
        self.insurance = insurance
        self.gift_wrap = gift_wrap


class Payee(RestObject):
    pass


class ItemList(RestObject):
    """
    For more Detaill:https://developer.paypal.com/docs/api/payments/#definition-item_list
    """

    def __init__(self, items=None, shipping_address=None, shipping_method=None, shipping_phone_number=None):
        """

        :param items: <Array: Item>
        :param shipping_address: <ShippingAddress>
        :param shipping_method: <str>
        :param shipping_phone_number: <str>
        :return:
        """
        self.items = items
        self.shipping_address = shipping_address
        self.shipping_method = shipping_method
        self.shipping_phone_number = shipping_phone_number


class ShippingAddress(RestObject):
    """
        For more: https://developer.paypal.com/docs/api/payments/#definition-shipping_address
    """

    def __init__(self, line1=None, line2=None, city=None, country_code=None, postal_code=None, state=None, phone=None,
                 _type=None, recipient_name=None):
        """

        :param line1: <str> Line 1 of the address (e.g., Number, street, etc). 100 characters max.
        :param line2: <str> Line 2 of the address (e.g., Suite, apt #, etc). 100 characters max.
        :param city: <str> City name. 50 characters max.
        :param country_code: <str> 2-letter country code. 2 characters max.
        :param postal_code: <str> Zip code or equivalent is usually required for countries that have them. 20 characters max.
                        Required in certain countries.
        :param state: <str> 2-letter code for US states, and the equivalent for other countries. 100 characters max.
        :param phone: <str> Phone number in E.123 format. 50 characters max.
        :param type: <str> Type of address (e.g., HOME_OR_WORK, GIFT etc).
        :param recipient_name: <str> Name of the recipient at this address. Maximum length: 127.
        :return:
        """
        self.line1 = line1
        self.line2 = line2
        self.city = city
        self.country_code = country_code
        self.postal_code = postal_code
        self.state = state
        self.phone = phone
        self.type = _type
        self.recipient_name = recipient_name


class Item(RestObject):
    """
        For more detail: https://developer.paypal.com/docs/api/payments/#definition-item
    """

    def __init__(self, sku=None, name=None, description=None, quantity=None, price=None, currency=None, tax=None,
                 url=None):
        """

        :param sku: <str> Stock keeping unit corresponding (SKU) to item. Maximum length: 127.
        :param name: <str> Item name. 127 characters max.
        :param description: <str> Description of the item. Only supported when the payment_method is set to paypal.
        :param quantity: <str> Number of a particular item. 10 characters max.
        :param price: <str> Item cost. 10 characters max.
        :param currency: <str> 3-letter currency code.
        :param tax: <str> Tax of the item. Only supported when the payment_method is set to paypal.
        :param url: <str> URL linking to item information. Available to payer in transaction history.
        :return:
        """
        self.sku = sku
        self.name = name
        self.description = description
        self.quantity = quantity
        self.price = price
        self.currency = currency
        self.tax = tax
        self.url = url


def dictionary_to_json_exclude_null(_dict):
    # serialize dict to json exclude None
    return json.dumps(dict((k, v) for k, v in _dict.items() if v is not None))
