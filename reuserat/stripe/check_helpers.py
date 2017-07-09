from django.conf import settings
import lob
import logging
from reuserat.static.images import check

# Get an instance of a logger
logger = logging.getLogger(__name__)

# TODO: Provide your API Key, keep this secure when we go live
lob.api_key = settings.LOB_TEST_API_KEY
# set an api version (optional)
lob.api_version = settings.LOB_API_VERSION


def create_check(customer_name, address_line1, address_line2, city, state, zipcode, country, amount):
    # Add this to the settings and import them here.
    try:
        from_address = lob.Address.create(
            description='Company Address',
            company=settings.COMPANY_NAME,
            address_line1=settings.COMPANY_ADDRESS_LINE,
            address_line2=settings.COMPANY_ADDRESS_LINE_APT,
            address_city=settings.COMPANY_CITY,
            address_state=settings.COMPANY_STATE,
            address_zip=settings.COMPANY_ZIP,
            address_country='US',
        )
        # Supplied via arguments
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

        logger.error("LOB Exception: " + str(e), exc_info=True)
        print('Failed to create from_address.')
        raise

    # TODO: Add a logo to your check
    # CHECK_LOGO = 'static/images/check/reuserat_logo.jpeg'

    # Print Mode & Creating check
    try:
        # Create Check
        check_response = lob.Check.create(
            description='Check for' + customer_name,
            to_address=to_address.id,
            from_address=from_address.id,
            bank_account=lob.BankAccount.list(limit=1, offset=0)['data'][0]['id'],
            # logo = open('reuserat_logo.jpeg', 'rb'),
            amount=amount,
            memo='test deposit',
        )

    except Exception as e:
        raise
    return check_response


def retrieve_tracking_number(check_id):
    check_response = lob.Check.retrieve(check_id)
    return check_response.tracking_number


def retrieve_all_bank_accounts():
    return lob.BankAccount.list(limit=2, offset=0)
