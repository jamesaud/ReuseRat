from test_plus.test import TestCase
from reuserat.users.tests.factories import UserFactory, EmailAddressFactory
from django.test import RequestFactory
from reuserat.users.views import UserDetailView
from django.test import override_settings
from reuserat.custom_middleware.middleware import FixMissingStripeAccountMiddleWare
from unittest.mock import Mock


@override_settings(MIDDLEWARE_CLASSES=(
    'reuserat.custom_middleware.middleware.FixMissingStripeAccountMiddleWare',
))
class TestFixMissingStripeAccount(TestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory()
        self.user.ssn_last_four = None
        self.user.save()
        self.factory = RequestFactory()
        mock_request = Mock()

        self.middleware = FixMissingStripeAccountMiddleWare(mock_request)
        self.view = UserDetailView  # Pick the dashboard view to see what happens to most users who login


    def test_middleware_working(self):
        self.assertTrue(self.user.stripe_account)
        self.assertTrue(self.user.paypal_account)
        request = self.factory.get('/fake-url')
        request.user = self.user
        response = self.middleware.__call__(request)
        self.assertIsNone(self.user.stripe_account)
        self.assertIsNone(self.user.paypal_account)


