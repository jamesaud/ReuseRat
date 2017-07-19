from test_plus.test import TestCase
from reuserat.users.tests.factories import BaseUserFactory, EmailAddressFactory
from django.test import RequestFactory
from reuserat.users.views import UserDetailView
from django.test import override_settings
from reuserat.custom_middleware.middleware import FixMissingStripeAccountMiddleWare
from unittest.mock import Mock

from django.conf import settings
import stripe

@override_settings(MIDDLEWARE_CLASSES=(
    'reuserat.custom_middleware.middleware.FixMissingStripeAccountMiddleWare',
))
class TestFixMissingStripeAccount(TestCase):
    def setUp(self):
        super().setUp()

        self.user = BaseUserFactory()
        self.factory = RequestFactory()
        mock_request = Mock()

        self.middleware = FixMissingStripeAccountMiddleWare(mock_request)
        self.view = UserDetailView  # Pick the dashboard view to see what happens to most users who login


    def test_middleware_working(self):
        self.assertIsNone(self.user.stripe_account)
        request = self.factory.get('/fake-url')
        request.user = self.user
        response = self.middleware.__call__(request)
        self.assertIsNotNone(self.user.stripe_account)


        stripe.api_key = settings.STRIPE_SECRET_KEY

        account = stripe.Account.retrieve(request.user.stripe_account.account_id)

        self.user = request.user
        self.assertEqual(account.legal_entity.first_name, self.user.first_name)
        self.assertEqual(account.legal_entity.last_name, self.user.last_name)
        self.assertEqual(account.legal_entity.address.line1, self.user.address.get_full_address_line())
        self.assertEqual(account.legal_entity.address.city, self.user.address.city)
        self.assertEqual(account.legal_entity.address.state, self.user.address.state)
        self.assertEqual(account.legal_entity.address.postal_code, self.user.address.zipcode)
        self.assertEqual(account.legal_entity.dob.day, self.user.birth_date.day)
        self.assertEqual(account.legal_entity.dob.month, self.user.birth_date.month)
        self.assertEqual(account.legal_entity.dob.year, self.user.birth_date.year)

