from django.test import TestCase
from django.conf import settings
import lob,stripe
from reuserat.users.tests import factories
from reuserat.stripe.helpers import create_account
from reuserat.stripe.tests.helpers import add_test_funds_to_account, add_test_funds_to_platform
from reuserat.stripe.check_helpers import create_check, retrieve_tracking_number


class TestCheckApi(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCheckApi, cls).setUpClass()
        lob.api_key = settings.LOB_TEST_API_KEY  # Platform Test API Key.
        lob.api_version = settings.LOB_API_VERSION
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Test Secret Key.
        cls.test_secret_key = settings.STRIPE_TEST_SECRET_KEY  # test.TEST_CUSTOMER_STRIPE_SECRET
        cls.user_object = factories.UserFactory()
        # Create Stripe account for cashing out
        cls.account = create_account('149.160.154.217')  # Stripe Account model instance
        add_test_funds_to_account(cls.account.account_id, 1000,
                                  'test_helpers.py in stripe app.')  # Add enough money to handle all the tests
        add_test_funds_to_platform(1000, 'test_helper.py in stripe app.')  # Add money to our platform
        customer_name = cls.user_object.get_full_name()
        address_line1 = cls.user_object.address.address_line
        address_line2 = cls.user_object.address.address_apartment
        city = cls.user_object.address.city
        state = cls.user_object.address.state
        zipcode = cls.user_object.address.zipcode
        country = cls.user_object.address.country
        amount = 1  # in dollars
        check = create_check(customer_name, address_line1, address_line2, city, state, zipcode, country,
                             amount)

    # Create Check:Success
    def test_success_create_check(self):
        customer_name = self.user_object.get_full_name()
        address_line1 = self.user_object.address.address_line
        address_line2 = self.user_object.address.address_apartment
        city = self.user_object.address.city
        state = self.user_object.address.state
        zipcode = self.user_object.address.zipcode
        country = self.user_object.address.country
        amount = 1  # in dollars
        check_response = create_check("customer", address_line1, address_line2, city, state, zipcode, country,
                                      amount)

        self.assertEqual(check_response.id, lob.Check.retrieve(check_response.id).id)
        self.assertTrue(check_response)

    # Create Check:Success
    def test_success_retrieve_tracking_number(self):
        tracking_number_response = retrieve_tracking_number(self.check.id)
        self.assertEqual(tracking_number_response,lob.Check.retrieve(self.check.id).tracking_number)
        self.assertTrue(tracking_number_response)

    # Create Check:Fail
    def test_success_retrieve_tracking_number(self):
        with self.assertRaises(lob.error.InvalidRequestError):
            test_tracking_number= retrieve_tracking_number("bad_key")



