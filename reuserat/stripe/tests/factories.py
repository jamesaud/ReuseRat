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
    account_id = 'replaced'
    user = None
    secret_key = 'replaced'
    publishable_key = 'replaced'

    class Meta:
        model = StripeAccount
        django_get_or_create = ('account_id', 'secret_key', 'publishable_key')

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        account =  _stripe_account_generator()
        self.account_id = account['id']
        self.secret_key = account['keys']['secret']
        self.publishable_key = account['keys']['publishable']


class PaypalAccountFactory(factory.django.DjangoModelFactory):
    email = factory.SubFactory("reuserat.users.tests.factories.EmailAddressFactory")

    class Meta:
        model = PaypalAccount
        django_get_or_create = ('email', )



