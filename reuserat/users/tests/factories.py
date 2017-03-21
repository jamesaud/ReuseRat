import factory
from factory import post_generation
import datetime
from reuserat.stripe.tests.factories import StripeAccountFactory, PaypalAccountFactory

from reuserat.users.models import Address, PaymentChoices, User

from allauth.account.models import EmailAddress

class AddressFactory(factory.django.DjangoModelFactory):
    address_line = "2661 East 7th Street"
    address_apartment = "D"
    city = "Bloomington"
    state = "IN"
    zipcode = "47408"
    country = "US"

    class Meta:
        model = Address



class EmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory('reuserat.users.tests.factories.UserFactory')
    verified = True
    primary = True
    email = factory.Sequence(lambda n: 'myuser{0}@test.com'.format(n))

    class Meta:
        model = EmailAddress


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    address = factory.SubFactory(AddressFactory)
    stripe_account = factory.SubFactory(StripeAccountFactory)
    first_name = factory.Sequence(lambda n: 'Jane-{0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Doe-{0}'.format(n))
    payment_type = PaymentChoices.CHECK
    phone = factory.Sequence(lambda n: '123-555-%04d' % n)
    birth_date  = datetime.date(2001, 5, 5)


    class Meta:
        model = User
        django_get_or_create = ('username', )

    # Create email associated with user - reverse foreign key relationship
    _email = factory.RelatedFactory(EmailAddressFactory, 'user')

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        # Set the paypal account to be assosciated with the user's email, with the email set above.
        self.paypal_account = PaypalAccountFactory(email=self.emailaddress_set.first())
