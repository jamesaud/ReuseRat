import factory
import datetime
from reuserat.stripe.tests.factories import StripeAccountFactory, PaypalAccountFactory
from reuserat.stripe.tests.helpers import add_test_funds_to_account, create_test_bank_token
from reuserat.stripe.helpers import update_payment_info

from ..models import Address, PaymentChoices, User

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


class BaseUserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    address = factory.SubFactory(AddressFactory)
    first_name = factory.Sequence(lambda n: 'Jane-{0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Doe-{0}'.format(n))
    payment_type = PaymentChoices.CHECK
    phone = factory.Sequence(lambda n: '123-555-%04d' % n)
    birth_date  = datetime.date(2001, 5, 5)

    class Meta:
        model = User
        django_get_or_create = ('username',)


class UserFactory(BaseUserFactory):
    stripe_account = factory.SubFactory(StripeAccountFactory)

    # Create email associated with user - reverse foreign key relationship
    _email = factory.RelatedFactory(EmailAddressFactory, 'user')

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        # Set the paypal account to be assosciated with the user's email, with the email set above.
        self.paypal_account = PaypalAccountFactory(email=self.emailaddress_set.first())


class UserRegisteredBankFactory(UserFactory):

    @factory.post_generation
    def post(self, create, extracted, **kwargs): # Can't use super, so wehave to repeat the setting of the paypal account
        self.paypal_account = PaypalAccountFactory(email=self.emailaddress_set.first())

        # Set the paypal account to be assosciated with the user's email, with the email set above.
        update_payment_info(account_id=self.stripe_account.account_id, account_token= create_test_bank_token(), user_object=self)





class FormUpdateUserFactory(dict):
    """Return the data in a dictionary needed for updating a user"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update({'first_name': 'test',
                     'last_name': 'test',
                     'payment_type': PaymentChoices.DIRECT_DEPOSIT,
                     'phone': '812-444-5555',
                     'birth_date_month': '5',
                     'birth_date_day': '5',
                     'birth_date_year': '2001',})


class FormUpdateUserAddressFactory(dict):
    """Return the data in a dictionary needed for updating a user"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update({'address_line': '504 e cottage grove',
                     'address_apartment': 5,
                     'city': 'bloomington',
                     'state': 'IN',
                     'zipcode': '47408'})

