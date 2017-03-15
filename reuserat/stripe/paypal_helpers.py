import paypalrestsdk
from paypalrestsdk import Payout, ResourceNotFound
from django.conf import settings

# Paypal Transfer function if user chooses Paypal Option
def make_payment_paypal(batch_id, receiver_email, amount, note):
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
                    "value": float(amount),
                    "currency": "USD"
                },
                "receiver": receiver_email,
                "note": note,
                "sender_item_id": "item_1"
            }
        ]
    })

    if payout.create(sync_mode=True):
        print("payout[%s] created successfully" %
              (payout.batch_header.payout_batch_id))
        return payout
    else:
        raise ValueError(payout.error)
