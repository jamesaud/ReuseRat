from django.conf import settings
from reuserat.stripe.models import StripeAccount

import stripe
import time

# Creating Managed Account in Stripe
def create_account(ip_addr=None):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # REAL KEY HERE

    acct = stripe.Account.create(
        managed=True,  # Managed Account
        country='US',
    )

    account = stripe.Account.retrieve(acct["id"])

    # Only if supplied, if not Stripe will ask for verification later.
    if ip_addr:
        account.tos_acceptance.date = int(time.time())
        account.tos_acceptance.ip = ip_addr  # Depends on what web framework you're using
    account.save()
    acct_instance = StripeAccount(account_id=acct['id'],
                                  secret_key=acct['keys']['secret'],
                                  publishable_key=acct['keys']['publishable'])
    acct_instance.save()
    return acct_instance


def retrieve_balance(secret_key):
    stripe.api_key = secret_key
    account_details = stripe.Balance.retrieve()
    return cents_to_dollars(account_details['available'][0]['amount'])


def update_payment_info(account_id, account_token, user_object):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # REAL KEY HERE
    account = stripe.Account.retrieve(account_id)

    # Update the display name for the account
    account.business_name = user_object.first_name

    # Update the display name for the account.
    account.business_name = user_object.get_full_name()

    # Update the address.
    account.legal_entity.address.line1 = user_object.address.address_line

    # If it is empty string, stripe will error.
    account.legal_entity.address.line2 = user_object.address.address_apartment or None
    account.legal_entity.address.city = user_object.address.city
    account.legal_entity.address.state = user_object.address.state
    account.legal_entity.address.country = "US"
    account.legal_entity.address.postal_code = user_object.address.zipcode

    account.legal_entity.dob.day = '{:02d}'.format(user_object.birth_date.day)
    account.legal_entity.dob.month = '{:02d}'.format(user_object.birth_date.month)
    account.legal_entity.dob.year = user_object.birth_date.year

    # Update First & Last names.
    account.legal_entity.first_name = user_object.first_name
    account.legal_entity.last_name = user_object.last_name

    account.legal_entity.type = "individual"

    # Save the account details
    account.save()

    # default_for_currency should be set as there can be multiple bank accounts
    # We set the newly created one as the default.
    account.external_accounts.create(external_account=account_token, default_for_currency="true")

    # Create Customer for each account
    stripe.Customer.create(
        description="Customer for " + user_object.get_full_name(),
        source=account_token  # obtained with Stripe.js
    )

    return account


def dollar_to_cent(dollar):
    cents = dollar * 100
    return cents


def cents_to_dollars(cents):
    return cents / 100


# Create a charge for an item on the Platform Account
def create_charge(account_id, amount_in_dollars, user_name):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # REAL KEY HERE
    # Stripe API call for Creating charge
    charge_details = stripe.Charge.create(
        amount=int(dollar_to_cent(amount_in_dollars * 0.50)),  # 50% of the amount is for the platform
        currency="usd",
        customer=settings.STRIPE_TEST_PLATFORM_CUSTOMER_ID,
        description="Hey " + user_name + " , you get $" + str( amount_in_dollars * 0.50),
        destination=account_id,
    )

    return charge_details['id']

# Making Transfer.Cash out the balance Stripe money for the customer
def create_transfer(account_id, balance_in_cents, user_name):

    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # REAL KEY HERE
    # Create Transfer

    if not isinstance(balance_in_cents, int):  # Don't want any rounding to happen if decimals come in
        raise ValueError("Cents must be an int")

    transfer = stripe.Transfer.create(
        currency="usd",
        amount = balance_in_cents,
        destination=account_id,
        description="Money transferred " + user_name,
    )
    return transfer['id']
