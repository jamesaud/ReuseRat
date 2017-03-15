from django.test import RequestFactory
from test_plus.test import TestCase
from reuserat.users.tests import factories
from unittest.mock import patch
import stripe
from django.conf import settings
from config.settings import test

from reuserat.stripe.helpers import create_charge

from ..models import PaymentChoices
from django.conf import settings
from .factories import EmailAddressFactory

from ..views import (
    UserRedirectView,
    UserUpdateView,
    cash_out,  # function based views
    UpdatePaymentInformation,
    UserCompleteSignupView

)


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
        # Expect: '/users/testuser/', as that is the default username for
        #   self.make_user()
        self.assertEqual(
            view.get_redirect_url(),
            '/users/testuser/'
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
        self.assertEqual(
            self.view.get_success_url(),
            '/users/testuser/'
        )


class TestUserCompleteSignup(TestCase):
    # Need to write test cases.
    # Test that other views redirect to this one if the user hasn't compelted signup.
    # Test the form submission on user complete signup.
    pass


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


class TestCashOut(TestCase):
    def setUp(self):
        self.factory = RequestFactory()  # Generate a mock request
        self.user = factories.UserFactory()  # Generate a mock user
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform test Secret Key.

    def test_get(self):
        # Create an instance of a GET request.
        request = self.factory.get('/~transfer/')

        # Cause factory doesn't support the middleware operations.
        request.user = self.user

        # Kat Valentine
        request.user.stripe_account.account_id = "acct_19vWYHLw2AVVFzC1"
        request.user.stripe_account.secret_key = "sk_test_gP7OiwFNaetrkV1DhVM9sim2"
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # REAL KEY HERE
        # Check if the form was rendered
        response = cash_out(request)
        self.assertEqual(response.status_code, 302)  # Html Code for Successful response
        
        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.SUCCESS = success = 'success'

        msg = u'Updated Bank Successfully'
        mock_messages = patch('reuserat.users.views.messages').start()
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
