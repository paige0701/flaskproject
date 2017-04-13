from apps.api_server.session_manager.base import BaseSession

__all__ = ['WirelessCheckoutSessionData', 'CheckoutSessionData']


class CheckoutSessionData(BaseSession):
    """
    Responsible for marshalling all the Checkout session data

    Multi-stage checkouts often require several forms to be submitted and their
    data persisted until the final order is placed. This class helps store and
    organise checkout form data until it is required to write out the final
    order.
        :keyword: namespace
        :key  shipping_data   ('shipping')
                :param - country : 국가
                :param - province : 주(광역자치단체)
                :param - address1 : 시(군,구)
                :param - address2 : 동
                :param - address3 : 나머지 주소
                :param - phone : 휴대폰(연락처)
                :param - method_code: 배송 방법 코드 (code, 무료)

        :key  billing_data   ('billing')
                :param - country : 국가
                :param - province : 주(광역자치단체)
                :param - address1 : 시(군,구)
                :param - address2 : 동
                :param - address3 : 나머지 주소
                :param - phone : 휴대폰(연락처)

        :key  payment_data   ('payment')
                :param - method : 결제 방법

        :key  products
                :param - items

        :key  order_data ('order')
                :param - method: 결제방법
    """

    # session Key MUST BE implemeted
    SESSION_KEY = "checkout_session"

    # Shipping address
    # ================
    # Options:
    # 1. No shipping required (eg. digital products)
    # 2. Ship to new address (entered in a form)
    # 3. Ship to an address book address (address chosen from list)

    def reset_shipping_data(self):
        """
        # namespace 'shipping' reset
        :return:
        """
        self._flush_namespace('shipping')

    def ship_to_user_address(self, address):
        """
        Use an user address ( from an address book) as the shipping address
        :param address: address Model
        :return:
        """
        self.reset_shipping_data()
        # address book에 존재하는 것
        self._set('shipping', 'user_address_id', address.id)

    def set_shipping_address(self, address):
        """
        address를 세션에 세팅
        :param address:  (need get function)
            - country
            - province
            - address1
            - address2
            - address3
            - phone
        :return:
        """
        self._check_namespace('shipping')
        for address_key in address:
            self.session[self.SESSION_KEY]['shipping'][address_key] = address[address_key]

    def get_dict_shipping_address(self):
        """
        :return: shipping_address
        :return :type : dict
        """

        return self.get_namespace_dict('shipping')

    def get_shipping_address(self):

        return self._get('shipping')

    def is_set_shipping_address(self):
        """
        Test whether a shipping address has been stored in the session.

        This can be from a new address or re-using an existing address.
        """
        self._check_namespace('shipping')

        shipping_key = ['country', 'state', 'city', 'line1', 'line2', 'phone']
        for address_key in self.session[self.SESSION_KEY]['shipping']:
            if address_key in shipping_key:
                shipping_key.remove(address_key)

        if not shipping_key:
            return True
        else:
            return False

    # Shipping method
    # ===============

    def use_free_shipping(self):
        """
        Set "free shipping" code to session
        무료배송
        """
        self._set('shipping', 'method_code', '__free__')

    def use_shipping_method(self, code):
        """
        Set shipping method code to session
        shipping method를 등록
        """
        self._set('shipping', 'method_code', code)

    def shipping_method_code(self):
        """
        Return the shipping method code
        shipping method를 가져옴
        """
        return self._get('shipping', 'method_code')

    def is_shipping_method_set(self):
        """
        Test if a valid shipping method is stored in the session
        """
        return self.shipping_method_code() is not None

    #  ------------------구분선------------------------
    # 여기까지 -- 윤수 캠퍼

    # Billing address fields
    # ======================
    # There are 3 common options:
    # 1. Billing address is entered manually through a form
    # 2. Billing address is selected from address book
    # 3. Billing address is the same as the shipping address

    def reset_billing_data(self):
        """
        # namespace 'shipping' reset
        :return:
        """
        self._flush_namespace('billing')

    def set_billing_address(self, address):
        """
        address를 세션에 세팅
        :param address:  (need x.get function)
            - country
            - province
            - address1
            - address2
            - address3
            - phone
        :return:
        """
        self._check_namespace('billing')
        for address_key in address:
            self.session[self.SESSION_KEY]['billing'][address_key] = address[address_key]

    def get_dict_billing_address(self):
        """
        :return: billing_address
        :return :type : dict
        """
        return self.get_namespace_dict('billing')

    def get_billing_address(self):
        return self._get('billing')

    def is_set_billing_address(self):
        """
        Test whether a billing address has been stored in the session.

        This can be from a new address or re-using an existing address.
        """
        self._check_namespace('billing')

        shipping_key = ['country', 'province', 'address1', 'address2', 'address3', 'phone']
        for address_key in self.session[self.SESSION_KEY]['billing']:
            if address_key in shipping_key:
                shipping_key.remove(address_key)

        if not shipping_key:
            return True
        else:
            return False

    # Payment methods
    # ===============
    def set_payment_method(self, method):
        self._set('payment', 'method', method)

    def get_payment_method(self):
        return self._get('payment', 'method')

    # products
    # ===============
    def set_product_list(self, product_list):
        """
        product의 list를 추가한다.
        각각의 product는 dictionar0y 이다.

        :type  list []
        :param product_list
            -[product1, product2, product3, ...]
                - product:
                    {'product_id' : product_number(int) - id(db)
                     'quantity': quantity,(int)
                    }
        """
        self._set('products', 'items', product_list)

    def get_product_list(self):
        return self._get('products', 'items')

    def add_product(self, product_item):
        self._check_namespace('products')
        self.session['products']['items'].append(product_item)

    def get_dict_product_list(self):
        return self.get_namespace_dict('products')

    # order
    # =================
    def set_order_method(self, order_method):
        """
        주문 방법을 택한다. (카트 결제인지, 즉시 주문인지 확인)
        :type str  (cart, direct)
        :param order_method
        """
        self._set('order', 'method', order_method)

    def get_order_method(self):
        """
        :return (cart or direct)
        """

        return self._get('order', 'method', None)



        # Submission methods
        # ==================

        # def set_order_number(self, order_number):
        #     self._set('submission', 'order_number', order_number)
        #
        # def get_order_number(self):
        #     return self._get('submission', 'order_number')
        #
        # def set_submitted_basket(self, basket):
        #     self._set('submission', 'basket_id', basket.id)
        #
        # def get_submitted_basket_id(self):
        #     return self._get('submission', 'basket_id')

        # Kamper 추가.
        # payment Detail Methods
        # ======================
        # def set_payment_detail_method(self, method):
        #     """
        #
        #     :param method: 'Alipay' or  'Paypal'
        #     :return:
        #     """
        #     self._set('payment_details', 'method', method)
        #
        # def get_payment_detail_method(self):
        #     return self._get('payment_details', 'method')

    def set_email(self, email):
        self._set('email', 'email', email)

    def get_email(self):
        return self._get('email', 'email')

    def set_order_number(self, order_id):
        order_number = 10000 + order_id
        self._set('order_number', 'order_number', order_number)

    def get_order_number(self):
        return self._get('order_number', 'order_number')

    def set_payment_unique_id(self, unique_id):
        self._set('payment', 'unique_id', unique_id)

    def get_payment_unique_id(self):
        return self._get('payment', 'unique_id')


class WirelessCheckoutSessionData(BaseSession):
    """
    [wireless Checkout Sessions]

    Responsible for marshalling all the WirelessCheckout session data

        :keyword: namespace
        :key  payment_data
                :param - type : 결제 품목 타입
                        1. sim : 심카드
                        2. charge : 충전
                        3. act_charge : 개통 및 충전

                :param - name : 결제 품목 이름

                :param - order_number : <order_number>

                :param - method: 결제 방법
                        1. paypal : 페이팔
                        2. alipay : 알리페이
                        3. transfer : 계좌이체

                :param - currency : 화폐
                :param - price : 금액

        :key  shipping_data   ('shipping')
                :param - country : 국가
                :param - province : 주(광역자치단체)
                :param - address1 : 시(군,구)
                :param - address2 : 동
                :param - address3 : 나머지 주소
                :param - phone : 휴대폰(연락처)
                :param - method_code: 배송 방법 코드 (code, 무료)




    """

    SESSION_KEY = "wireless_checkout_session"

    wireless_order_type = ('sim', 'recharge', 'act_charge',)

    def reset_payment_data(self):
        """
        # namespace 'payment' reset
        :return:
        """
        self._flush_namespace('payment_data')

    def _set_payment_type(self, _type):
        self._set('payment_data', 'type', _type)



    def _set_payment_method(self, method):
        self._set('payment_data', 'method', method)

    def _set_name(self, name):
        self._set('payment_data', 'name', name)

    def _set_currency(self, currency):
        self._set('payment_data', 'currency', currency)

    def _set_price(self, price):
        self._set('payment_data', 'price', price)

    def _set_order_number(self, order_number):
        self._set('payment_data', 'order_number', order_number)

    def _set_phone(self, phone_number):
        self._set('payment_data', 'phone', phone_number)

    def _set_email(self, email):
        self._set('payment_data', 'email', email)

    def set_wireless_product(self, type, name, order_number, payment_method, currency, price, phone_number=None, email=None):
        if type not in self.wireless_order_type:
            raise ValueError("wireless product에는 제한된 값만 들어갑니다. ('sim', 'recharge', 'act_charge',) ")
        self._set_payment_type(type)
        self._set_name(name)
        self._set_order_number(order_number)
        self._set_payment_method(payment_method)
        self._set_currency(currency)
        self._set_price(price)
        self._set_phone(phone_number)
        self._set_email(email)




    def reset_shipping_data(self):
        """
        # namespace 'shipping' reset
        :return:
        """
        self._flush_namespace('shipping_data')
