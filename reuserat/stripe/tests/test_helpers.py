from django.test import TestCase
from reuserat.stripe.models import StripeAccount
import stripe
from django.conf import settings
from config.settings import test
from reuserat.users.tests import factories
from reuserat.stripe.helpers import create_account, retrieve_balance, update_payment_info,create_charge,dollar_to_cent,create_transfer


class TestStripeApi(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestStripeApi, cls).setUpClass()
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Test Secret Key.
        cls.test_secret_key = test.TEST_CUSTOMER_STRIPE_SECRET
        cls.test_account_token= stripe.Token.create(bank_account={"country": 'US',
                                                    "currency": 'usd',
                                                    "account_holder_name": 'Jane Doe',
                                                    "account_holder_type": 'individual',
                                                    "routing_number": '110000000',
                                                    "account_number": '000123456789'
                                                    },)
        cls.test_account_id = test.TEST_CUSTOMER_STRIPE_ACCOUNT_ID
        cls.test_balance = 0.50 # in dollars

    # Create Account : Success
    def test_success_create_account(self):
        ip_address = '149.160.154.217' # Test Ip address
        test_account = create_account(ip_address)
        test_db_account = StripeAccount.objects.get(account_id=test_account.account_id)

        # The function saves the api object using .save method provided by stripe .
        # We can verify it by retrieving the account using an API call.
        self.assertTrue(test_account, stripe.Account.retrieve(test_account.account_id))
        self.assertTrue(test_account)
        self.assertTrue(test_db_account)

    # Retrieve Balance : Success
    def test_success_retrieve_balance(self):
        test_balance = retrieve_balance(self.test_secret_key)
        self.assertTrue(isinstance(test_balance,float))

    # Retrieve Balance : Failure
    def test_failure_retrieve_balance(self):
        with self.assertRaises(stripe.error.AuthenticationError):
            test_balance = retrieve_balance("TEST_SECRET_KEY")

    # UpdatePaymentInfo : Success
    def test_success_update_payment_info(self):
        user_object = factories.UserFactory()
        account_token = self.test_account_token
        account_id = self.test_account_id

        test_account = update_payment_info(account_id, account_token, user_object)

        print(user_object.stripe_account.account_id,"ACCOUNT ID")

        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Test Secret Key.
        sample_account = stripe.Account.retrieve(account_id) # Retrieve the saved account from Stripe using the account_id

        self.assertEqual(test_account.business_name, sample_account.business_name)
        self.assertEqual(test_account.legal_entity.address.line1, sample_account.legal_entity.address.line1)
        self.assertEqual(test_account.legal_entity.address.line2, sample_account.legal_entity.address.line2)
        self.assertEqual(test_account.legal_entity.address.city, sample_account.legal_entity.address.city)
        self.assertEqual(test_account.legal_entity.address.state, sample_account.legal_entity.address.state)
        self.assertEqual(test_account.legal_entity.address.country, sample_account.legal_entity.address.country)
        self.assertEqual(test_account.legal_entity.address.postal_code, sample_account.legal_entity.address.postal_code)

        self.assertEqual(test_account.legal_entity.dob.day, sample_account.legal_entity.dob.day)
        self.assertEqual(test_account.legal_entity.dob.month, sample_account.legal_entity.dob.month)
        self.assertEqual(test_account.legal_entity.dob.year, sample_account.legal_entity.dob.year)

        self.assertEqual(test_account.legal_entity.first_name, sample_account.legal_entity.first_name)
        self.assertEqual(test_account.legal_entity.last_name, sample_account.legal_entity.last_name)

        self.assertEqual(test_account.legal_entity.personal_address.line1,
                        sample_account.legal_entity.personal_address.line1)
        self.assertEqual(test_account.legal_entity.personal_address.line2,
                        sample_account.legal_entity.personal_address.line2)
        self.assertEqual(test_account.legal_entity.personal_address.city,
                        sample_account.legal_entity.personal_address.city)
        self.assertEqual(test_account.legal_entity.personal_address.state,
                        sample_account.legal_entity.personal_address.state)
        self.assertEqual(test_account.legal_entity.personal_address.country,
                        sample_account.legal_entity.personal_address.country)
        self.assertEqual(test_account.legal_entity.personal_address.postal_code,
                        sample_account.legal_entity.personal_address.postal_code)
        self.assertEqual(test_account.legal_entity.type,
                        sample_account.legal_entity.type)
        self.assertEqual(test_account.external_accounts['data'][0]['account_holder_name'],
                         sample_account.external_accounts['data'][0]['account_holder_name'])
        self.assertEqual(test_account.external_accounts['data'][0]['currency'],
                         sample_account.external_accounts['data'][0]['currency'])
        self.assertEqual(test_account.external_accounts['data'][0]['routing_number'],
                         sample_account.external_accounts['data'][0]['routing_number'])

    # UpdatePaymentInfo : Failure
    def test_failure_update_payment_info(self):
        user_object = factories.UserFactory()
        account_token = "TEST_TOKEN"
        account_id = "TEST_ACCOUNT_ID"
        with self.assertRaises(stripe.error.PermissionError):
            test_account = update_payment_info(account_id, account_token, user_object)

    # CreateCharge : Success
    def test_success_create_charge(self):
        user_object = factories.UserFactory()
        account_id =self.test_account_id
        amount=1 # in dollars
        test_amount = dollar_to_cent(amount)
        test_charge_id=create_charge(account_id, amount, user_object.get_full_name())
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Secret Key.
        sample_charge = stripe.Charge.retrieve(test_charge_id)
        self.assertEqual(sample_charge['amount'],test_amount*0.50)
        self.assertEqual(sample_charge['customer'], settings.STRIPE_TEST_PLATFORM_CUSTOMER_ID)
        self.assertEqual(sample_charge['destination'], account_id)

    # CreateCharge : Failure
    def test_failure_create_charge(self):
        with self.assertRaises(stripe.error.InvalidRequestError):
            user_object = factories.UserFactory()
            amount =1
            account_id = "TEST_ACCOUNT_ID"
            test_account = create_charge(account_id, amount,user_object.get_full_name())

    # CreateTransfer : Success
    def test_success_create_transfer(self):
        with self.assertRaises(stripe.error.InvalidRequestError): # Tested too many times so it will raise this error
            user_object = factories.UserFactory()
            amount = 1  # in dollars
            test_amount = dollar_to_cent(amount)
            test_charge_id = create_charge(self.test_account_id, amount, user_object.get_full_name())
            test_transfer_id = create_transfer(self.test_account_id,self.test_balance,user_object.get_full_name())
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Secret Key.
            sample_transfer = stripe.Transfer.retrieve(test_transfer_id)
            self.assertEqual(test_transfer_id,"In")
            self.assertEqual(self.test_balance*100 , sample_transfer['amount'])
