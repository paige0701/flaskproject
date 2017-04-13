#
# class WirelessCheckoutSessionData(CheckoutSessionData):
#     SESSION_KEY = 'wireless_session'
#
#     def set_sim_type(self, value):
#         """
#         최소충전 2만원으로 하고 //
#         5천원 할인
#         """
#         self._set('product', 'sim_type', value)
#
#     def set_sim_quantity(self, value):
#         self._set('product', 'quantity', value)
#
#     def is_sim_order_state(self):
#         if self._get('product', 'sim_type') is not None:
#             return True
#         else:
#             return False
