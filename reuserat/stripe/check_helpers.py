from django.conf import settings
from reuserat.stripe.models import StripeAccount

import stripe
import time
import lob,json
import logging
from reuserat.static.images import check

# Get an instance of a logger
logger = logging.getLogger(__name__)

# TODO: Provide your API Key, keep this secure when we go live
lob.api_key = settings.LOB_TEST_API_KEY
# set an api version (optional)
lob.api_version = '2016-06-30'


def create_check(customer_name, address_line1, address_line2, city, state, zipcode, country,amount):
    # Add this to the settings and import them here.
    try:
        from_address = lob.Address.create(
            description='Company Address',
            name='Reuse Rat',
            company='Reuse Rat',
            address_line1='504 E Cottage Grove',
            address_line2='Apt #5',
            address_city='Bloomington',
            address_state='IN',
            address_zip='47408',
            address_country='US',
        )
        to_address = lob.Address.create(
            description='Customer Address',
            name=customer_name,
            address_line1=address_line1,
            address_line2=address_line2,
            address_city=city,
            address_state=state,
            address_zip=zipcode,
            address_country=country,
        )

    except Exception as e:

        logger.error("LOB Exception: " + str(e))
        print('Failed to create from_address.')
        raise

    print("Agriculture", from_address)
    print("Computer", to_address)

    # TODO: Create and verify your bank account
    try:
        bank_account = lob.BankAccount.create(
            description='Test Bank Account',
            routing_number='322271627',
            account_number='123456789',
            account_type='company',
            signatory='John Doe'
        )

    except Exception as e:
        logger.error("LOB Exception: " + str(e))
        print('Failed to create bank account')
        raise

    print("JOBS", bank_account)
    try:
        example_bank_account = lob.BankAccount.verify(id=bank_account.id, amounts=[23, 77])
        print("BANK ACCOUNT",example_bank_account)
    except Exception as e:
        print('Error: ' + str(e))
        print('Failed to verify bank account.')
        raise

    # TODO: Add a logo to your check
    # CHECK_LOGO = 'static/images/check/reuserat_logo.jpeg'

    # Print Mode & Creating check
    try:
        # Print mode to screen
        # mode = lob.api_key.split('_')[0]
        # print('Sending checks in ' + mode.upper() + ' mode.')

        # Create Check
        check_response = lob.Check.create(
            description='Demo Check for' + customer_name,
            to_address=to_address.id,
            from_address=from_address.id,
            bank_account=example_bank_account.id,
            #logo = open('reuserat_logo.jpeg', 'rb'),
            amount=amount,
            memo='test deposit',
            check_bottom='<h1 style="padding-top:4in;">Demo Check for {{name}}</h1>',
        )

    except Exception as e:
        print('Error: ' + str(e))
        print('Failed to create check')
        raise
    print("CHECKSSSSS", check_response)
    return check_response

