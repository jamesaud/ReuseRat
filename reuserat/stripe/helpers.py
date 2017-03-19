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

    account.transfer_schedule.interval = 'manual'
    account.save()

    acct_instance = StripeAccount(account_id=acct['id'],
                                  secret_key=acct['keys']['secret'],
                                  publishable_key=acct['keys']['publishable'])
    acct_instance.save()
    return acct_instance


def retrieve_balance(secret_key):
    stripe.api_key = secret_key
    account_details = stripe.Balance.retrieve()
    return account_details['available'][0]['amount']


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
    account.external_accounts.create(external_account=account_token,
                                     default_for_currency="true",)

    # Create Customer for each account
   # stripe.Customer.create(
   #     description="Customer for " + user_object.get_full_name(),
   #     source=account_token  # obtained with Stripe.js
   # )

    return account


def dollars_to_cents(dollar):
    return dollar * 100


def cents_to_dollars(cents):
    return cents / 100


# Create a charge for an item on the Platform Account
def create_charge(account_id, amount_in_cents, user_name):
    """
    Transfers money from OUR Stripe account to a customer's.
    :param account_id: The user's Stripe account id
    :param amount_in_dollars: The amount to charge
    :param user_name: The user's username, as a description for the charge.
    :return: String, the id of the charge.
    """
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # REAL KEY HERE
    # Stripe API call for Creating charge
    charge_details = stripe.Charge.create(
        amount=int(amount_in_cents),  # 50% of the amount is for the platform
        currency="usd",
        customer=settings.STRIPE_TEST_PLATFORM_CUSTOMER_ID,  # Our Stripe Account Customer ID
        description="Hey " + user_name + " , you get $" + str(amount_in_cents),
        destination=account_id,
    )

    return charge_details['id']


def create_transfer_bank(account_id, balance_in_cents, user_name):
    """
    # Cash out a user's Stripe balance to their bank account.
    :param account_id:  User's bank account id.
    :param account_secret_key: The user's stripe account secret key.
    :param balance_in_cents: Amount to cash out
    :param user_name: User's user name
    :return: String, transfer id
    """

    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Customer Secret Key

    if not isinstance(balance_in_cents, int):  # Don't want any rounding to happen if it is a Float.
        raise ValueError("Cents must be an int")

    transfer = stripe.Transfer.create(
        amount=balance_in_cents,
        currency="usd",
        description="Money transferred to bank account for: " + user_name,
        destination="default_for_currency",
        stripe_account=account_id,
        source_type="bank_account",
    )

    return transfer['id']


def create_transfer_to_us(account_id, balance_in_cents, user_name):
    """
    Transfers money from one Stripe account to another Stripe account using Stripe secret keys.
    :return:
    """
    pass


def test_mode_add_funds():
    pass
