import factory
from django.conf import settings
from reuserat.stripe.models import StripeAccount, PaypalAccount
import stripe, time


def _stripe_account_generator():
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    return stripe.Account.create(
        managed=True,
        country='US',
        external_account={
            'object': 'bank_account',
            'country': 'US',
            'currency': 'usd',
            'routing_number': '110000000',
            'account_number': '000123456789',
        },
        tos_acceptance={
            'date': int(time.time()),
            'ip': "64.134.34.193",
        },
    )

class StripeAccountFactory(factory.django.DjangoModelFactory):
    account_id = _stripe_account_generator().id

    secret_key = settings.STRIPE_TEST_SECRET_KEY
    publishable_key = settings.STRIPE_TEST_PUBLISHABLE_KEY

    class Meta:
        model = StripeAccount
        django_get_or_create = ('account_id', 'secret_key', 'publishable_key')


class PaypalAccountFactory(factory.django.DjangoModelFactory):
    email = factory.SubFactory("reuserat.users.tests.factories.EmailAddressFactory")

    class Meta:
        model = PaypalAccount
        django_get_or_create = ('email', )



