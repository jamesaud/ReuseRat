import factory

from reuserat.stripe.models import StripeAccount

class StripeAccountFactory(factory.django.DjangoModelFactory):
    account_id = factory.Sequence(lambda n: 'acct_19pm6VHg9CVh6B0c{0}'.format(n))
    #account_number_token = "btok_A7xzZwdCO5Bw1J"

    secret_key = "sk_test_JcKuBl55h46qCdt7IEVMveu2"
    publishable_key = "pk_test_GfhkFHmANH7UkBCPaybmdTYF"

    class Meta:
        model = StripeAccount
        django_get_or_create = ('account_id','secret_key', 'publishable_key')
