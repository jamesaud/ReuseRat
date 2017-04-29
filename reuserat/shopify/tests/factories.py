import factory
import json
from reuserat.shipments.tests.factories import ShipmentFactory

class ItemFactory(factory.django.DjangoModelFactory):
    id = factory.Sequence(lambda n: 'item-{0}'.format(n))
    name = factory.Sequence(lambda n: 'item-name-{0}'.format(n))
    handle = factory.Sequence(lambda n: 'item-{0}-handle'.format(n))
    is_visible = True
    shipment = factory.SubFactory(ShipmentFactory)  # Shipment is a foreign key, so we must use SubFactory
    data = json.loads(
        '{"id":327475578523353102,"title":"Example T-Shirt","body_html":null,"vendor":"Acme","product_type":"Shirts","created_at":null,"handle":"example-t-shirt","updated_at":null,"published_at":"2017-02-11T20:47:55-05:00","template_suffix":null,"published_scope":"global","tags":"mens t-shirt example","variants":[{"id":1234567,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-s","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":null,"option1":"Small","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":75,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":75,"requires_shipping":true},{"id":1234568,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-m","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":"shopify","option1":"Medium","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":50,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":50,"requires_shipping":true}],"options":[{"id":12345,"product_id":null,"name":"Title","position":1,"values":["Small","Medium"]}],"images":[{"id":1234567,"product_id":327475578523353100,"position":0,"created_at":null,"updated_at":null,"src":"//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png","variant_ids":[]}],"image":null}'
        )

    class Meta:
        model = 'shopify.Item'
        django_get_or_create = ('id',)


class ItemOrderDetailsFactory(factory.django.DjangoModelFactory):
    item = factory.RelatedFactory(ItemFactory)
    transfer_id = factory.Sequence(lambda n: n)
    order_data = {}

    class Meta:
        model = 'shopify.ItemOrderDetails'
