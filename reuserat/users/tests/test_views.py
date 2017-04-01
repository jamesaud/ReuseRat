from django.test import RequestFactory
from test_plus.test import TestCase
from reuserat.users.tests import factories
from unittest.mock import patch
from config.settings import test
from django.conf import settings

from reuserat.stripe import helpers as stripe_helpers
from reuserat.stripe.models import Transaction, TransactionTypeChoices, StripeAccount, PaypalAccount
from reuserat.stripe.tests.helpers import add_test_funds_to_account
import lob
from ..models import PaymentChoices
from .factories import EmailAddressFactory, FormUpdateUserFactory, FormUpdateUserAddressFactory

from ..views import (
    UserRedirectView,
    UserUpdateView,
    CashOutView,  # function based views
    UpdatePaymentInformation,
    UserCompleteSignupView
)

import stripe

class BaseUserTestCase(TestCase):
    def setUp(self):
        self.user = self.make_user()
        self.factory = RequestFactory()


class TestUserRedirectView(BaseUserTestCase):
    def test_get_redirect_url(self):
        # Instantiate the view directly. Never do this outside a test!
        view = UserRedirectView()
        # Generate a fake request
        request = self.factory.get('/fake-url')
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        view.request = request
        #   self.make_user()
        self.assertEqual(
            view.get_redirect_url(),
            '/dashboard/'
        )


class TestUserUpdateView(BaseUserTestCase):
    def setUp(self):
        # call BaseUserTestCase.setUp()
        super(TestUserUpdateView, self).setUp()
        # Instantiate the view directly. Never do this outside a test!
        self.view = UserUpdateView()
        # Generate a fake request
        request = self.factory.get('/fake-url')
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        self.view.request = request

    def test_get_success_url(self):
        # Expect: '/users/testuser/', as that is the default username for
        #   self.make_user()
        self.assertEqual(self.view.get_success_url(), '/dashboard/')


class TestUserCompleteSignup(BaseUserTestCase):
    def setUp(self):
        super(TestUserCompleteSignup, self).setUp()
        self.view = UserCompleteSignupView
        EmailAddressFactory(user=self.user)  # Add a valid email to the user, which happens prior to update view
        # Post data to be submitted as Dict like objects
        self.user_update_data = FormUpdateUserFactory()
        self.user_address_data = FormUpdateUserAddressFactory()
        self.request = self.factory.post(path='/~complete_signup/',
                                    data={**self.user_update_data, **self.user_address_data}) # Merge dicts
        self.request.user = self.user



    def test_fields_added(self):
        user_update_data, user_address_data = self.user_update_data, self.user_address_data

        user = self.request.user
        response = self.view.as_view()(self.request)

        # Make sure the user was updated appropriately
        self.assertEqual(user.first_name, user_update_data['first_name'])
        self.assertEqual(user.last_name, user_update_data['last_name'])
        self.assertEqual(user.payment_type, user_update_data['payment_type'])
        self.assertEqual(user.phone, user_update_data['phone'])

        self.assertEqual(user.address.address_line, user_address_data['address_line'])
        self.assertEqual(user.address.address_apartment, str(user_address_data['address_apartment']))
        self.assertEqual(user.address.city, user_address_data['city'])
        self.assertEqual(user.address.state, user_address_data['state'])
        self.assertEqual(user.address.zipcode, user_address_data['zipcode'])

    def test_stripe_paypal_added(self):
        response = self.view.as_view()(self.request)

        # Stripe and Paypal should execute without error
        stripe_account = StripeAccount.objects.get(user=self.user)
        paypal_account = PaypalAccount.objects.get(email=self.user.emailaddress_set.all().first())

class TestUpdatePaymentInformation(TestCase):
    def setUp(self):
        self.factory = RequestFactory()  # Generate a mock request
        self.user = factories.UserFactory()  # Generate a mock user
        account = self.user.stripe_account
        account.account_id = test.TEST_CUSTOMER_STRIPE_ACCOUNT_ID  # Test Stripe account id
        account.save()
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform test Secret Key.

    def test_get(self):
        # Create an instance of a GET request.
        request = self.factory.get('/~updatepayment/')

        # Cause it doesn't support the middleware operations.
        request.user = self.user

        # Check if the form was rendered
        response = UpdatePaymentInformation.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_stripe_updated(self):
        account_number = settings.STRIPE_TEST_ACCOUNT_NUMBER
        routing_number = settings.STRIPE_TEST_ROUTING_NUMBER
        account_name = 'Jane Doe'

        form_data = {
            'payment_type': PaymentChoices.DIRECT_DEPOSIT,
            'account_holder_name': account_name,
            'currency': 'USD',
            'birth_date_month': '5',
            'birth_date_day': '5',
            'birth_date_year': '2001',
            'routing_number': routing_number,
            'account_number': account_number,
            'account_holder_type': 'individual',
            'country': 'US',
            'birthdate_day': '5',
            'stripeToken': stripe.Token.create(bank_account={"country": 'US',
                                                             "currency": 'USD',
                                                             "account_holder_name": account_name,
                                                             "account_holder_type": 'individual',
                                                             "routing_number": routing_number,
                                                             "account_number": account_number
                                                             }, )['id']
        }

        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.SUCCESS = success = 'success'

        request = self.factory.post('/~updatepayment/', data=form_data)
        request.user = self.user
        response = UpdatePaymentInformation.as_view()(request)

        self.assertEqual(response.status_code, 302)  # Html Code for Redirection

        mock_messages.SUCCESS = success = 'success'

        msg = u'Updated Bank Successfully'
        mock_messages.add_message.assert_called_with(request, success, msg)

        self.assertEqual(account_number[-4:], self.user.stripe_account.account_number_last_four)
        self.assertEqual(routing_number[-4:], self.user.stripe_account.routing_number_last_four)
        self.assertEqual(len(account_number), self.user.stripe_account.account_number_length)
        self.assertEqual(account_name, self.user.stripe_account.account_holder_name)
        self.assertTrue(self.user.stripe_account.has_bank())
        self.assertTrue(self.user.payment_type, PaymentChoices.DIRECT_DEPOSIT)


    def test_paypal_account(self):
        """
        Test that the email submitted becomes the user's paypal account's new email.
        """
        new_email = EmailAddressFactory(user=self.user)

        form_data = {
            'payment_type': PaymentChoices.PAYPAL,
            'email': new_email.email,
        }

        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.SUCCESS = success = 'success'

        request = self.factory.post('/~updatepayment/', data=form_data)
        request.user = self.user
        response = UpdatePaymentInformation.as_view()(request)

        msg = u'Updated Paypal Successfully'
        mock_messages.add_message.assert_called_with(request, success, msg)

        self.assertEqual(self.user.paypal_account.email, new_email)
        self.assertEqual(self.user.payment_type, PaymentChoices.PAYPAL)
        self.assertEqual(302, response.status_code)

        # This test should fail, because the email is not one of the user's verified emails.
        fail_email = 'fail@test.com'
        form_data_fail = {
            'payment_type': PaymentChoices.PAYPAL,
            'email': fail_email,
        }

        request = self.factory.post('/~updatepayment/', data=form_data_fail)
        request.user = self.user
        response = UpdatePaymentInformation.as_view()(request)

        self.assertNotEqual(fail_email, request.user.paypal_account.email)

    def test_check_updated(self):
        form_data = {
            'payment_type': PaymentChoices.CHECK,
        }

        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.SUCCESS = success = 'success'

        request = self.factory.post('/~updatepayment/', data=form_data)
        request.user = self.user
        response = UpdatePaymentInformation.as_view()(request)

        msg = u'Updated Check Successfully'
        mock_messages.add_message.assert_called_with(request, success, msg)

        self.assertEqual(self.user.payment_type, PaymentChoices.CHECK)




class TestCashOut(TestCase):
    def setUp(self):
        self.factory = RequestFactory()  # Generate a mock request
        self.user = factories.UserRegisteredBankFactory()  # Generate a mock user
        self.request = self.factory.post('/~cashout/')
        self.request.user = self.user
        add_test_funds_to_account(self.user.stripe_account.account_id, 100, 'test_my_cash_out_setup') # Add a dollar before each cash out test.

    def _assert_transaction_cash_out_test(self, old_balance):
        """Run after each cash_out test to make sure that the correct Transaction object is created."""
        transaction_object = Transaction.objects.get(user=self.request.user)
        self.assertEqual(transaction_object.user, self.request.user)
        self.assertEqual(transaction_object.payment_type, self.request.user.payment_type)
        self.assertEqual(transaction_object.type, TransactionTypeChoices.OUT)
        self.assertEqual(transaction_object.amount, stripe_helpers.cents_to_dollars(old_balance))


    def test_cashout_direct_deposit(self):
        """Check that the correct stripe funds are transfered to a user's bank account."""
        self.request.user.payment_type = PaymentChoices.DIRECT_DEPOSIT
        self.request.user.save()

        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.SUCCESS = success = 'success'
        msg = 'Cashed out using Direct Deposit successfully. Check the status at My Account > Transactions'

        old_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)
        response = CashOutView.as_view()(self.request)
        new_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)

        mock_messages.add_message.assert_called_with(self.request, success, msg)

        self.assertGreater(old_balance, 0)
        self.assertEqual(0, new_balance)
        self._assert_transaction_cash_out_test(old_balance)



    def test_cashout_paypal(self):

        """Check that the correct stripe funds are transfered to the user's paypal acount"""
        self.request.user.payment_type = PaymentChoices.PAYPAL
        email = EmailAddressFactory(email=settings.PAYPAL_SANDBOX_BUYER_EMAIL, user=self.request.user)  # Set to a valid Paypal email during testing
        self.request.user.paypal_account.email = email
        self.request.user.paypal_account.save()

        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.SUCCESS = success = 'success'
        msg = 'Cashed out using Paypal successfully. Please accept the email sent to {}. To resend the email, please go to My Account > Transactions.'.format(self.request.user.paypal_account.email.email)


        old_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)
        response = CashOutView.as_view()(self.request)

        mock_messages.add_message.assert_called_with(self.request, success, msg)

        new_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)

        self.assertGreater(old_balance, 0)
        self.assertEqual(new_balance, 0)
        self._assert_transaction_cash_out_test(old_balance)


    def test_fail_cashout_paypal(self):

        """Check that the correct stripe funds are transfered to the user's paypal acount"""
        self.request.user.payment_type = PaymentChoices.PAYPAL
        email = EmailAddressFactory(email='unverifiedemail1929304219470@gmail.com', user=self.request.user)  # Set to a valid Paypal email during testing
        self.request.user.paypal_account.email = email
        self.request.user.paypal_account.save()

        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.ERROR = error = 'error'
        msg = "Paypal Account using email {} doesn't exist or is unregistered! Please add an existing Paypal email or contact support.".format(self.request.user.paypal_account.email.email)

        old_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)
        response = CashOutView.as_view()(self.request)

        mock_messages.add_message.assert_called_with(self.request, error, msg)

        new_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)

        self.assertGreater(old_balance, 0)
        self.assertEqual(new_balance, old_balance) # Balance should not change! Refund via Stripe should be called.
        with self.assertRaises(Transaction.DoesNotExist): # If a cashout fails, transaction object should not exsist
            Transaction.objects.get(user=self.request.user)


    def test_cashout_check(self):

        """Check that the correct stripe funds are transfered"""
        self.request.user.payment_type = PaymentChoices.CHECK

        old_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)
        response = CashOutView.as_view()(self.request)
        new_balance = stripe_helpers.retrieve_balance(self.user.stripe_account.secret_key)
        self.assertGreater(old_balance, 0)
        self.assertEqual(new_balance, 0)
        self._assert_transaction_cash_out_test(old_balance)
        transaction_object = Transaction.objects.get(user=self.request.user)
        self.assertEqual(lob.Check.retrieve(transaction_object.check_id).to_address.name,self.request.user.get_full_name())
        self.assertEqual(lob.Check.retrieve(transaction_object.check_id).to_address.address_line1, self.request.user.address.address_line)
        self.assertEqual(lob.Check.retrieve(transaction_object.check_id).to_address.address_line2,
                         self.request.user.address.address_apartment)

        self.assertEqual(lob.Check.retrieve(transaction_object.check_id).to_address.address_line2,
                         self.request.user.address.address_apartment)

        self.assertEqual(lob.Check.retrieve(transaction_object.check_id).to_address.address_city,
                         self.request.user.address.city)
        self.assertEqual(lob.Check.retrieve(transaction_object.check_id).to_address.address_state,
                         self.request.user.address.state)
        self.assertEqual(lob.Check.retrieve(transaction_object.check_id).to_address.address_zip,
                         self.request.user.address.zipcode)



