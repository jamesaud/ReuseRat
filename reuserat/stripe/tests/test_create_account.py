from django.test import TestCase
from reuserat.stripe.models import StripeAccount
import stripe
from django.conf import settings
from reuserat.users.tests import factories
from reuserat.stripe.helpers import create_account, retrieve_balance, update_payment_info


class TestStripeApi(TestCase):
    def test_success_create_account(self):
        ip_address = '149.160.154.217'
        test_account = create_account(ip_address)
        test_db_account = StripeAccount.objects.get(account_id=test_account["id"])

        # The function saves the api object using .sae method provided by stripe .
        # We can verify it by retrieving the account using an API call.
        self.assertTrue(test_account, stripe.Account.retrieve(test_account["id"]))

        self.assertTrue(test_account)
        self.assertTrue(test_db_account)

    # Retrieve Balance : Success
    def test_success_retrieve_balance(self):
        test_balance = retrieve_balance(settings.STRIPE_TEST_SECRET_KEY)
        self.assertTrue(test_balance)

    # Retrieve Balance : Fail
    def test_failure_retrievebalance(self):
        test_balance = retrieve_balance("TEST_SECRET_KEY")
        self.assertFalse(test_balance)

    def test_success_update_payment_info(self):
        user_object = factories.UserFactory()
        account_token = "btok_A7xzZwdCO5Bw1J"
        account_id = user_object.stripe_account.account_id
        test_account = update_payment_info(account_id, account_token, user_object)
        sample_account = stripe.Account.retrieve(account_id)
        self.assertEqual(test_account.display_name, sample_account.display_name)

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
        self.assertEqual(test_account.external_accounts,
                        sample_account.external_accounts)

        test_db_account = StripeAccount.objects.get(account_number_token=account_token)

        self.assertTrue(test_account)
        self.assertTrue(test_db_account)

    def test_failure_update_payment_info(self):
        user_object = factories.UserFactory()
        account_token = "TEST_TOKEN"
        account_id = "TEST_ACCOUNT_ID"
        test_account = update_payment_info(account_id, account_token, user_object)
        self.assertFalse(test_account)
