import paypalrestsdk
from paypalrestsdk import Payout, ResourceNotFound
from django.conf import settings




"""
Define our Paypal Exception Class, for the different types of Paypal errors that can arise.
"""
class PaypalException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    @classmethod
    def new(cls, name):
        """
        Create a new exception of type "Paypal Exception"
        :return:
        """
        return type(name, (cls,), {})  # Create a new class, inheriting from parent class.


# Paypal Transfer function if user chooses Paypal Option
def make_payment_paypal(batch_id, receiver_email, amount_in_dollars, note):
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox for testing or live
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_SECRET })

    payout = Payout({
        "sender_batch_header": {
            "sender_batch_id": batch_id,
            "email_subject": "You have a payment"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": float(amount_in_dollars),
                    "currency": "USD"
                },
                "receiver": receiver_email,
                "note": note,
                "sender_item_id": "item_1"
            }
        ]
    })

    if payout.create(sync_mode=True):
        error = payout.items[0].errors
        if error:
            error_class = PaypalException.new(error.name)  # New error class based on the type of Paypal Error
            raise error_class(error.message)
        else:
            return payout
    else:
        raise PaypalException(payout.error)
