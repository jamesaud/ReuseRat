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
    def new(cls, name, prefix=True):
        """
        Create a new exception of type "Paypal Exception"
        Prefix is used to auto-generate the Paypal error name. It comes in as 'RECEIVER_UNREGISTERED', converts to 'PaypalReceiverUnregistered'
        :return:
        """
        pythonic_name = 'Paypal' + name.title().replace("_",'') if prefix else name
        return type(pythonic_name, (cls,), {})  # Create a new class, inheriting from parent class.


class PaypalReceiverUnregistered(PaypalException):
    """A user isn't registered with Paypal"""
    pass


# Paypal responds with the following codes that we want to catch.
__PaypalErrorLookup = {
    'RECEIVER_UNREGISTERED': PaypalReceiverUnregistered,
}



# Paypal Transfer function if user chooses Paypal Option
def make_payment_paypal(batch_id, receiver_email, amount_in_dollars, note):
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,  # sandbox for testing or live
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
                "sender_item_id": "1"
            }
        ]
    })

    if payout.create(sync_mode=True):
        print("PAYING OUT")
        print(payout)
        error = payout.items[0].errors
        if error:
            # Lookup tohe error class, or create New error class based on the type of Paypal Error
            error_class = __PaypalErrorLookup.get(error.name, None) or PaypalException.new(error.name)
            raise error_class(error.message)
        else:
            return payout
    else:
        raise __PaypalErrorLookup.get(payout.error, None) or PaypalException(payout.error)
