from django.conf import settings
from reuserat.stripe.models import StripeAccount

import stripe
import time



import logging

from config.logging import setup_logger

setup_logger()
logger = logging.getLogger(__name__)



# Creating Managed Connected Account in Stripe
def create_account(ip_addr=None):
    """
    Creates a Stripe Connected account for the user, and creates an instance of StripeAccount in our DB.
    :param ip_addr: The ip_address of the user, used to sign the Connected Stripe Account agreement.
    :return: StripeAccount, an object from the model StripeAccount
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY  # REAL KEY HERE

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

    logger.error("In stripe/helpers.py/create_account -- account created",account)
    acct_instance.save()
    return acct_instance


def retrieve_balance(secret_key):
    stripe.api_key = secret_key
    account_details = stripe.Balance.retrieve()
    return account_details['available'][0]['amount']


def update_payment_info(account_id, account_token, user_object):
    stripe.api_key = settings.STRIPE_SECRET_KEY  # REAL KEY HERE
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

    ### Commented out, as Stripe returns an error: "You cannot change `legal_entity[first_name]` via API if an account is verified."
    account.legal_entity.first_name = account.legal_entity.first_name or user_object.first_name
    account.legal_entity.last_name = account.legal_entity.last_name or user_object.last_name

    account.legal_entity.type = "individual"

    account.external_accounts.create(external_account=account_token,
                                     default_for_currency=True, )
    logger.error("In stripe/helpers.py/update_payment_info --- Updated Payment Info stripe,and actual thing", account.legal_entity.address.line2,user_object.address.address_apartment)
    logger.error("In stripe/helpers.py/update_payment_info --- Updated Payment Info stripe,and actual thing",account.legal_entity.address.city, user_object.address.city)
    logger.error("In stripe/helpers.py/update_payment_info --- and actual thing",user_object.address,user_object.birth_date,user_object.first_name)
    account.save()
    return account['id']


def dollars_to_cents(dollar):
    return dollar * 100


def cents_to_dollars(cents):
    return cents / 100


def create_transfer_bank(api_key, balance_in_cents, user_name):
    """
    # Cash out a user's Stripe balance to their bank account.
    :param account_id:  User's bank account id.
    :param account_secret_key: The user's stripe account secret key.
    :param balance_in_cents: Amount to cash out
    :param user_name: User's user name
    :return: String, transfer id
    """

    stripe.api_key = api_key  # Customer Secret Key

    if not isinstance(balance_in_cents, int):  # Don't want any rounding to happen if it is a Float.
        raise ValueError("Cents must be an int")

    transfer = stripe.Transfer.create(
        amount=balance_in_cents,
        currency="usd",
        description="Money transferred to bank account for: " + user_name,
        destination="default_for_currency",
        source_type='bank_account'
    )

    return transfer['id']


# Confusingly named function, because it's not transfering to a Stripe Customer.
# It's transfering to a user with an account_id.
def create_transfer_to_customer(account_id, balance_in_cents, description):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if not isinstance(balance_in_cents, int):  # Don't want any rounding to happen if it is a Float.
        raise ValueError("Cents must be an int")

    transfer = stripe.Transfer.create(
        amount=balance_in_cents,
        currency="usd",
        description=description,
        source_type='bank_account',
        destination=account_id)

    return transfer['id']


def create_transfer_to_platform(account_id, balance_in_cents, description):
    """
    Transfers money from a connected Stripe account to our Platform Stripe account.
    :return:
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    platform_account_id = stripe.Account.retrieve().id

    if not isinstance(balance_in_cents, int):  # Don't want any rounding to happen if it is a Float.
        raise ValueError("Cents must be an int")

    transfer = stripe.Transfer.create(
        amount=balance_in_cents,
        currency="usd",
        description=description,
        destination=platform_account_id,
        stripe_account=account_id,
        source_type='bank_account'
    )
    return transfer['id']


def reverse_transfer(transfer_id, api_key=None):
    """
    :param transfer_id: String, the id of the transfer
    :param api_key: String, optionally the api key of the connected account. Will use the platform api key if not using account
    :return:
    """
    stripe.api_key = api_key or settings.STRIPE_SECRET_KEY
    transfer = stripe.Transfer.retrieve(transfer_id)
    reversal = transfer.reversals.create()
    return reversal['id']


