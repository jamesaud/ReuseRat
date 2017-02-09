import factory
from reuserat.users.tests.factories import UserFactory


class ShipmentFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'shipment-{0}'.format(n))
    description = factory.Sequence(lambda n: 'shipment-{0}-description'.format(n))

    user = factory.SubFactory(UserFactory)  # User is a foreign key, so we must use SubFactory

    class Meta:
        model = 'shipments.Shipment'
        django_get_or_create = ('name',)



