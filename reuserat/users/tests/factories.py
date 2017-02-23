import factory
import datetime
from reuserat.stripe.tests.factories import StripeAccountFactory
from reuserat.users.models import Address

class AddressFactory(factory.django.DjangoModelFactory):
    address_line = "2661 East 7th Street"
    address_apartment = "D"
    city = "Bloomington"
    state = "IN"
    zipcode = "47408"
    country = "US"

    class Meta:
        model= Address


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    address = factory.SubFactory(AddressFactory)

    stripe_account = factory.SubFactory(StripeAccountFactory)
    first_name = "Jane"
    last_name = "Doe"
    payment_type = "Check"
    phone = factory.Sequence(lambda n: '123-555-%04d' % n)
    birth_date =  birthdate = factory.Sequence(lambda n: datetime.date(2000, 1, 1) + datetime.timedelta(days=n))

    class Meta:
        model = 'users.User' # Avoid the complications of a circular import
        django_get_or_create = ('username', )
