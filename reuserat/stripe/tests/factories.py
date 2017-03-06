import factory

from django.conf import settings

from reuserat.stripe.models import StripeAccount, PaypalAccount

class StripeAccountFactory(factory.django.DjangoModelFactory):
    account_id = factory.Sequence(lambda n: 'acct_19pm6VHg9CVh6B0c{0}'.format(n))
    #account_number_token = "btok_A7xzZwdCO5Bw1J"

    secret_key = settings.STRIPE_TEST_SECRET_KEY
    publishable_key = settings.STRIPE_TEST_PUBLISHABLE_KEY

    class Meta:
        model = StripeAccount
        django_get_or_create = ('account_id','secret_key', 'publishable_key')


class PaypalAccountFactory(factory.django.DjangoModelFactory):
    email = factory.SubFactory("reuserat.users.tests.factories.EmailAddressFactory")

    class Meta:
        model = PaypalAccount
        django_get_or_create = ('email', )

