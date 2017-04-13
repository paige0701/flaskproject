import os

from apps import app
from apps.api_server.payment.models import Order,OrderLineItem,Payment
import paypalrestsdk
#
# paypalrestsdk.configure({
#     "mode": "live", # sandbox or live
#     "client_id": "ASbP8_MmvNEjDM2-n18gsAiN838_Wwj-XRKFxe4T2n0VlXimNMzQujHrMFINp3RkrNyX3bbhRDzYLK-2",
#     "client_secret": "EGxchYlAC0zUY0GAaJoXqzS8yPxoT7ntCy5ZPquaO5U4Qsz27ufeE-PC4w4IoF7PGN2kt6C7QIe8mU_S"})

paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": "AX9oticVoE9-gmiQv0W3Hab-tRhZ7IHBNqWFHIUSCZBOf7UctIl885M6e8W6CG3liSAbnbsLoK3Wv0Ue",
    "client_secret": "EGJe8MBHABjqPEPQTZh3rU5-TbxnYYA7tMI6XZNaewSQInkG6oZmXhRv_Qs6pq9McHOYaS3BZvdX05ij"})


def create_payment(items, intent, payer ,transactions=None, experience_profile_id=None, amount=None,details=None, shipping_address=None, payer_info=None,
                   return_url='execute', cancel_url='cancel'):

    base_url = app.config.get('BASE_URL')

    return_url = os.path.join(base_url,return_url)
    cancel_url = os.path.join(base_url,cancel_url)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        # Payer
        # A resource representing a Payer that funds a payment
        # Payment Method as 'paypal'
        "payer": {
            "payment_method": "paypal",

            "payer_info":
            #     {
            #     "email": "npurayil-uspr-60@paypal.com",
            #     "first_name": "Brian",
            #     "last_name": "Robinson",
            #     "payer_id": "JMKDKJ4D7DG7G",
            #
            #
            # },
                payer_info,
            # Transaction
            # A transaction defines the contract of a
            # payment - what is the payment for and who
            # is fulfilling it.

        }, # Redirect URLs
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{

            # ItemList
            "item_list": {
                "items": items,
                "shipping_address":
                #     "line1": "4thFloor",
                #     "line2": "unit#34",
                #     "city": "SAn Jose",
                #     "state": "CA",
                #     "postal_code": "95131",
                #     "country_code": "US",
                #     "phone": "011862212345678",
                #     "recipient_name": "HelloWorld"
                # }
                    shipping_address
            },

            # Amount
            # Let's you specify a payment amount.
            "amount": {
                "total": amount,
                "currency": "USD",
                "details":
                    details
            },
            "description": "This is the payment transaction description.",
        }]
    })

    print("페이먼트 정보 : ", payment)
    # Create Payment and return status
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Redirect the user to given approval url
        return payment
    else:
        print("Error while creating payment:")
    print(payment.error)


def execute_payment(payment_id,payer_id):
    # ID of the payment. This ID is provided when creating payment.
    payment = paypalrestsdk.Payment.find(payment_id)
    print(payment)
    # PayerID is required to approve the payment.
    if payment.execute({"payer_id":payer_id }):  # return True or False


        print("Payment[%s] execute successfully" % (payment.id))

    else:
        print(payment.error)

    return payment