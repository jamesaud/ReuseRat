from reuserat.stripe.models import StripeAccount

import stripe
from django.conf import settings
import time


# Creating Managed Account in Stripe
def create_account(ip_addr=None):

    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY # REAL KEY HERE

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


def dollar_to_cent(dollar):
    cents = dollar * 100
    return cents

def cents_to_dollars(cents):
    return cents/100

def retrieve_balance(secret_key):
    stripe.api_key = secret_key
    account_details = stripe.Balance.retrieve()
    print(account_details,"ACCOUNT DETAILS")
    return cents_to_dollars(account_details['available'][0]['amount'])



def update_payment_info(account_id, account_token, user_object):

    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Secret Key.
    account = stripe.Account.retrieve(account_id)
    # Update the display name for the account.
    account.business_name = user_object.first_name

    # # Update the address.
    account.legal_entity.address.line1 = user_object.address.address_line
    account.legal_entity.address.line2 = user_object.address.address_apartment
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

    # Update personal address field.
    account.legal_entity.personal_address.line1 = user_object.address.address_line
    account.legal_entity.personal_address.line2 = user_object.address.address_apartment
    account.legal_entity.personal_address.city = user_object.address.city
    account.legal_entity.personal_address.state = user_object.address.state
    account.legal_entity.personal_address.country = "US"
    account.legal_entity.personal_address.postal_code = user_object.address.zipcode

    account.legal_entity.type = "individual"

    # Save the account details
    account.save()
    account.external_accounts.create(external_account=account_token, default_for_currency="true")
    return account

#Create a charge
def create_charge(account_id,amount):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY # REAL KEY HERE

    charge = stripe.Charge.create(
        amount = int(dollar_to_cent(float(amount) * 0.50)),
        currency = "usd",
        customer = settings.STRIPE_TEST_PLATFORM_CUSTOMER_ID,
        description = "Hey random customer ,I paid you",
        #destination={"account": account_id},
    )
    print("Charge details",charge)
    return charge['id']

# Making Transfer.Cash out the balance Stripe money for the customer
def create_transfer(account_id,balance):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # REAL KEY HERE
    print("HULK,I AM HERE?",account_id)
    transfer = stripe.Transfer.create(
            currency="usd",
            amount = int(balance*100),
            destination=account_id,
            description="the random customer got the Payment,Thank you",
        )
    print(transfer['id'])


        # # Create the Token first
    # token = stripe.Token.create(
    #     bank_account={
    #         "country": 'US',
    #         "currency": 'usd',
    #         "account_holder_name": "Jose Doe",
    #         "account_holder_type": 'individual',
    #         "routing_number": "110000000",
    #         "account_number": "000123456789"
    #     },
    # )
    # # Create the customer
    # customer = stripe.Customer.create(
    #     source=token,
    #     description="test customer"
    # )
    #

    # print(customer,"LISTEEENNNNNNNN",customer["sources"]["data"][0]["id"])
    # customer = stripe.Customer.retrieve(customer["id"])
    # bank_account = customer.sources.retrieve(customer["sources"]["data"][0]["id"])

    # verify the account
   # bank_account.verify(amounts=[32, 45])

    # charge = stripe.Charge.create(
    #     amount=100,
    #     currency="usd",
    #     customer=customer["id"],
    #     description="Hey Maya Jenner ,I paid you"
    # )
    #print("CHARGE DETAILS",charge)
    # transfer = stripe.Transfer.create(
    #     amount=100, #in cents
    #     currency="usd",
    #     destination="default_for_currency",
    #     stripe_account=account_id,
    #     source_type = "bank_account",
    # )
    # print("TRANSFER DETAILS", charge)
    # print("TEST, i AM HERE")
# def create_charge(user_obj, acc_token=None,):
#     stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Secret Key.
#
#     charge = stripe.Charge.create(
#         amount=500,
#         currency="usd",
#         source="tok_19lNzxIPg8ix8N5WIe1eVxkv",
#     )
#     print("CHARGE", charge)
#     # Create Transfer
#     transfer = stripe.Transfer.create(
#         amount=70,
#         currency="usd",
#         destination=user_obj.stripe_account.account_id,  # Connected Stripe Account id
#     )
#

# def update_acco# def update_account_details(account_id,fieldName)
#     acct_details = stripe.Account.retrieve(account_id)
#     acct_details.support_phone = "555-867-5309"
#     acct_details.save()
#     print(acct_details,"AAAAAAAAAAAAAAAAAAAAA")
#     return HttpResponse(acct_details)unt_details(account_id,fieldName)
#     acct_details = stripe.Account.retrieve(account_id)
#     acct_details.support_phone = "555-867-5309"
#     acct_details.save()
#     print(acct_details,"AAAAAAAAAAAAAAAAAAAAA")
#     return HttpResponse(acct_details)
#
