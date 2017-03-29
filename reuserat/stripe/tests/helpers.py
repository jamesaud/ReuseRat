from django.conf import settings
import stripe




def create_test_bank_token():
    return stripe.Token.create(bank_account={"country": 'US',
                                                    "currency": 'usd',
                                                    "account_holder_name": 'Jane Doe',
                                                    "account_holder_type": 'individual',
                                                    "routing_number": '110000000',
                                                    "account_number": '000123456789'
                                                    },)


# Create a test charge to a test customer and deposit it into an account
def add_test_funds_to_account(account_id, amount_in_cents, description):
    """
    Add money to a test account. We don't want the money to show up under 'card' in 'source_types', we want it to show up
    under 'bank_account'. In order for this to happen, we have to follow verify a test bank account. In production, it will
    be our verified account.
    Docs: https://stripe.com/docs/ach#creating-an-ach-charge
    :param account_id: The user's Stripe account id
    :param amount_in_dollars: The amount to charge
    :param user_name: The user's username, as a description for the charge.
    :return: String, the id of the charge.
    """
    if not isinstance(amount_in_cents, int):  # Don't want any rounding to happen if it is a Float.
        raise ValueError("Cents must be an int")

    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    # Create a temporary customer and verify the bank account
    customer = stripe.Customer.create(
        source=create_test_bank_token(),
        description="Example customer"
    )
    bank = customer.sources['data'][0]
    bank.verify(amounts=[32, 45])

    # Stripe API call for adding money from a bank account to the user's account.
    charge_details = stripe.Charge.create(
        amount=amount_in_cents,
        currency="usd",
        customer = customer.id,
        description=description,
        destination=account_id
    )

    return charge_details['id']

def add_test_funds_to_platform(amount_in_cents, description):
    """
    Add money to a test account. We don't want the money to show up under 'card' in 'source_types', we want it to show up
    under 'bank_account'. In order for this to happen, we have to follow verify a test bank account. In production, it will
    be our verified account.
    Docs: https://stripe.com/docs/ach#creating-an-ach-charge
    :param account_id: The user's Stripe account id
    :param amount_in_dollars: The amount to charge
    :param user_name: The user's username, as a description for the charge.
    :return: String, the id of the charge.
    """
    if not isinstance(amount_in_cents, int):  # Don't want any rounding to happen if it is a Float.
        raise ValueError("Cents must be an int")

    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    # Create a temporary customer and verify the bank account
    customer = stripe.Customer.create(
        source=create_test_bank_token(),
        description="Example customer"
    )
    bank = customer.sources['data'][0]
    bank.verify(amounts=[32, 45])

    # Stripe API call for adding money from a bank account to the user's account.
    charge_details = stripe.Charge.create(
        amount=amount_in_cents,
        currency="usd",
        customer = customer.id,
        description=description,
    )

    return charge_details['id']
