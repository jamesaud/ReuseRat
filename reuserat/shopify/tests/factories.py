import factory
from reuserat.shipments.tests.factories import ShipmentFactory


class ItemFactory(factory.django.DjangoModelFactory):
    id = factory.Sequence(lambda n: int('{}'.format(n)))
    name = factory.Sequence(lambda n: 'shipment-{0}'.format(n))
    handle = factory.Sequence(lambda n: 'shipment-{0}-handle'.format(n))

    shipment = factory.SubFactory(ShipmentFactory)  # Shipment is a foreign key, so we must use SubFactory

    class Meta:
        model = 'shopify.Item'
        django_get_or_create = ('id', )



