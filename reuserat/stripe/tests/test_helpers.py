from django.test import TestCase
from reuserat.stripe.models import StripeAccount
import stripe
from django.conf import settings
from config.settings import test
from reuserat.users.tests import factories
from reuserat.stripe.helpers import (create_account, retrieve_balance, update_payment_info, reverse_transfer,
                                      create_transfer_to_customer, create_transfer_to_platform, create_transfer_bank)
from reuserat.stripe.tests.helpers import add_test_funds_to_account, create_test_bank_token, add_test_funds_to_platform


class TestStripeApi(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestStripeApi, cls).setUpClass()
        stripe.api_key = settings.STRIPE_SECRET_KEY  # Platform Test Secret Key.
        cls.test_secret_key = settings.STRIPE_SECRET_KEY # test.TEST_CUSTOMER_STRIPE_SECRET
        # Tokens are unique, so we lambda it to create a new token each time. Needs to take 1 argument because it's called with self
        cls.account = create_account('149.160.154.217') # Stripe Account model instance


        add_test_funds_to_account(cls.account.account_id, 1000, 'test_helpers.py in stripe app.') # Add enough money to handle all the tests
        add_test_funds_to_platform(1000, 'test_helper.py in stripe app.') # Add money to our platform

    # Create Account : Success
    def test_success_create_account(self):
        ip_address = '149.160.154.217'
        test_account = create_account(ip_address)
        test_db_account = StripeAccount.objects.get(account_id=test_account.account_id)

        # The function saves the api object using .save method provided by stripe .
        # We can verify it by retrieving the account using an API call.
        self.assertEqual(test_account.account_id, stripe.Account.retrieve(test_account.account_id).id)
        self.assertTrue(test_account)
        self.assertTrue(test_db_account)

    # Retrieve Balance : Success
    def test_success_retrieve_balance(self):
        test_balance = retrieve_balance(self.test_secret_key)
        self.assertTrue(isinstance(test_balance, int))

    # Retrieve Balance : Failure
    def test_failure_retrieve_balance(self):
        with self.assertRaises(stripe.error.AuthenticationError):
            test_balance = retrieve_balance("bad_key")

    # UpdatePaymentInfo : Success
    def test_success_update_payment_info(self):
        user_object = factories.UserFactory(stripe_account=self.account)
        account_token = create_test_bank_token()
        account_id = self.account.account_id
        stripe.api_key = settings.STRIPE_SECRET_KEY  # Platform Test Secret Key.

        test_account_id = update_payment_info(account_id, account_token, user_object)
        test_account = stripe.Account.retrieve(test_account_id)

        sample_account = stripe.Account.retrieve(account_id) # Retrieve the saved account from Stripe using the account_id

        # It is redundant, I know, but we get to verify that all of these fields were set in the update function.
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

        self.assertEqual(test_account.legal_entity.personal_address.line1, sample_account.legal_entity.personal_address.line1)
        self.assertEqual(test_account.legal_entity.personal_address.line2, sample_account.legal_entity.personal_address.line2)
        self.assertEqual(test_account.legal_entity.personal_address.city, sample_account.legal_entity.personal_address.city)
        self.assertEqual(test_account.legal_entity.personal_address.state, sample_account.legal_entity.personal_address.state)
        self.assertEqual(test_account.legal_entity.personal_address.country, sample_account.legal_entity.personal_address.country)
        self.assertEqual(test_account.legal_entity.personal_address.postal_code, sample_account.legal_entity.personal_address.postal_code)
        self.assertEqual(test_account.legal_entity.type, sample_account.legal_entity.type)

        self.assertEqual(test_account.external_accounts['data'][0]['account_holder_name'], sample_account.external_accounts['data'][0]['account_holder_name'])
        self.assertEqual(test_account.external_accounts['data'][0]['currency'], sample_account.external_accounts['data'][0]['currency'])
        self.assertEqual(test_account.external_accounts['data'][0]['routing_number'], sample_account.external_accounts['data'][0]['routing_number'])

    # UpdatePaymentInfo : Failure
    def test_failure_update_payment_info(self):
        user_object = factories.UserFactory()
        account_token = "FAIL_TOKEN"
        account_id = "FAIL_ACCOUNT_ID"
        with self.assertRaises(stripe.error.PermissionError):
            test_account = update_payment_info(account_id, account_token, user_object)

    # CreateCharge : Success
    def test_success_create_transfer_to_customer(self):
        account_id = self.account.account_id
        transfer_amount = 100  # in cents

        old_balance_platform, old_balance_user = retrieve_balance(settings.STRIPE_SECRET_KEY), retrieve_balance(self.account.secret_key) # Get platform balance
        transfer_id = create_transfer_to_customer(account_id, transfer_amount, "test_sucess_create_transfer_to_customer")
        new_balance_platform, new_balance_user = retrieve_balance(settings.STRIPE_SECRET_KEY), retrieve_balance(self.account.secret_key)

        transfer = stripe.Transfer.retrieve(transfer_id, api_key=settings.STRIPE_SECRET_KEY) # Log in as the customer

        self.assertEqual(transfer['amount'], transfer_amount)
        self.assertEqual(transfer['destination'], account_id)
        self.assertEqual(transfer['destination'], account_id)

        print(stripe.Balance.retrieve())

        self.assertEqual(old_balance_platform - transfer_amount, new_balance_platform) # Our stripe account lost money
        self.assertEqual(old_balance_user + transfer_amount, new_balance_user) # User gained money


    # CreateTransfer : Success
    def test_success_create_transfer_to_platform(self):
        transfer_amount = 100
        account_id = self.account.account_id

        old_balance_platform, old_balance_user = retrieve_balance(settings.STRIPE_SECRET_KEY), retrieve_balance(self.account.secret_key) # Get platform balance
        transfer_id = create_transfer_to_platform(account_id, transfer_amount, 'test_success_create_transfer_to_platform') # Transfer 1 dollar
        new_balance_platform, new_balance_user = retrieve_balance(settings.STRIPE_SECRET_KEY), retrieve_balance(self.account.secret_key)
        transfer = stripe.Transfer.retrieve(transfer_id)

        self.assertEqual(transfer_id, transfer['id'])
        self.assertEqual(old_balance_platform + transfer_amount , new_balance_platform) # Our stripe account gained money
        self.assertEqual(old_balance_user - transfer_amount, new_balance_user) # The user account lost money


    def test_create_transfer_bank(self):
        transfer_amount = 100

        # Update the account with a bank account.
        user_object = factories.UserFactory(stripe_account=self.account)
        account_token = create_test_bank_token()

        update_payment_info(self.account.account_id, account_token, user_object)
        print(stripe.Balance.retrieve(api_key=self.account.secret_key))
        stripe.api_key = settings.STRIPE_SECRET_KEY  # Platform Test Secret Key.
        old_balance_user = retrieve_balance(self.account.secret_key)
        transfer_id = create_transfer_bank(self.account.secret_key, transfer_amount, "test_create_transfer_bank")
        new_balance_user = retrieve_balance(self.account.secret_key)

        transfer = stripe.Transfer.retrieve(transfer_id, api_key=self.account.secret_key)

        self.assertEqual(new_balance_user, old_balance_user - transfer_amount)
        self.assertEqual(transfer['amount'], transfer_amount)

    def test_reverse_transfer(self):
        transfer_amount = 100
        transfer_id = create_transfer_to_platform(self.account.account_id, transfer_amount, "test_reverse_transfer")
        reverse_id = reverse_transfer(transfer_id, api_key=self.account.secret_key)
        transfer = stripe.Transfer.retrieve(transfer_id, api_key=self.account.secret_key)
        self.assertEqual(transfer['amount'], transfer['amount_reversed'])
        self.assertTrue(transfer['reversed'])

    def test_add_test_funds_to_account(self):
        stripe.api_key = self.account.secret_key
        old_balance = retrieve_balance(self.account.secret_key)
        add_test_funds_to_account(self.account.account_id, 100, 'test_add_test_funds_to_account')
        new_balance = retrieve_balance(self.account.secret_key)

        self.assertEqual(old_balance+100, new_balance)
