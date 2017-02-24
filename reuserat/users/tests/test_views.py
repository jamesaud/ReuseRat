from django.test import RequestFactory
from test_plus.test import TestCase
from reuserat.users.tests import factories
from unittest.mock import patch
import stripe
from django.conf import settings
from ..views import (
    UserRedirectView,
    UserUpdateView,
    update_payment_information,
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

    def test_get_object(self):
        # Expect: self.user, as that is the request's user object
        self.assertEqual(
            self.view.get_object(),
            self.user
        )

class TestUpdate_Payment_Information(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.factory = RequestFactory()
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Platform Secret Key.

    def test_get(self):
        # Create an instance of a GET request.
        request = self.factory.get('/~updatepayment/')

        # Cause it doesnt support the middleware operations.
        request.user = self.user

        # Check if the form was rendered
        response = update_payment_information(request)

        self.assertEqual(response.status_code, 200)

    def test_post(self):

        form_data = {'account_holder_name': 'Jane Doe',
                     'currency': 'USD',
                     'birthdate_month': '5',
                     'birthdate_year': '2001',
                     'routing_number': '111000025',
                     'account_number': '000123456789',
                     'account_holder_type': 'individual',
                     'country': 'US',
                     'birthdate_day': '5',
                     'stripeToken':stripe.Token.create(bank_account={"country": 'US',
                                                                "currency": 'USD',
                                                                "account_holder_name": 'Jane Doe',
                                                                "account_holder_type": 'individual',
                                                                "routing_number": '111000025',
                                                                "account_number": '000123456789'
                                                                }, )['id']
                     }
        #requests.post(settings.BASE_URL + '/api/project', params=data)
        mock_messages = patch('reuserat.users.views.messages').start()
        mock_messages.SUCCESS = success = 'success'
        request = self.factory.post('/~updatepayment/',data = form_data)
        request.user = self.user
        response = update_payment_information(request)
        msg = u'Updated'
        mock_messages.add_message.assert_called_with(request, success, msg)

        #request.user= self.user
        # Check if the form was rendered

        self.assertEqual(response.status_code, 302)





