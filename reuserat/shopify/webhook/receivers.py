from reuserat.shopify.models import Item
from reuserat.shipments.models import Shipment
from ..helpers import valid_sku

'''
RECEIVERS FOR WEBHOOK SIGNALS ARE DEFINED BELOW.
ROUTING IS IN APPS.PY

Improve:
 - create JSON validation templates which we can verify: http://python-jsonschema.readthedocs.io/en/latest/validate/
'''

class AbstractShopifyReceiver:

    @staticmethod
    def _get_shopify_json(json_sender_data):
        return json_sender_data['data']  # parse out the sender signal and name



class ProductReceivers(AbstractShopifyReceiver):

    """
    Using Item instead of Product because that's what our Model is called.
    """

    @classmethod
    def item_create(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        shipment = cls._get_shipment(shopify_json)  # Get the related shipment, specified in 'SKU'
        item = Item(data=shopify_json, id=shopify_json.get('id'), shipment=shipment)
        item.save()
        print("\n\nSAVED THAT ITEM @@@@\n\n\n")

    @classmethod
    def item_update(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        item = cls._get_item(shopify_json)
        item.data = shopify_json
        item.save()


    @classmethod
    def item_update_or_create(cls, sender, **kwargs):
        try:
            cls.item_update(sender ,**kwargs)
        except Item.DoesNotExist:
            cls.item_create(sender, **kwargs)

    @classmethod
    def item_delete(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        item = cls._get_item(shopify_json)
        item.delete()


    """
    Helper Functions Below
    """


    @classmethod
    def _get_item(self, json_data):
        try:
            item = Item.objects.get(pk=json_data['id'])
        except Item.DoesNotExist:
            print("Getting item using primary key found from 'id' in json does not exist: {}".format(json_data))
            raise
        return item


    @classmethod
    def _get_shipment(cls, json_data):
        try:
            id = cls._get_shipment_id(json_data)
            return Shipment.objects.get(pk=id)
        except Shipment.DoesNotExist:
            print("Shipment with ID + does not exist in database from json_data: {}".format(json_data))
            raise

    @classmethod
    def _get_shipment_id(cls, json_data):
        # The first variant's SKU, which is the same as all variants SKU.
        # Split on dash because the SKU is entered in as:   "<userid> - <shipment_id>"
        if valid_sku(json_data.get('variants')[0].get('sku')):
            return json_data.get('variants')[0].get('sku').split('-')[1]
        raise ValueError("JSON sku is not formatted as expected: {}".format(json_data))

    @classmethod
    def _get_user_id(cls, json_data):
        # The first variant's sku, which is the same as all variants sku
        # Split on dash because the SKU is entered in as:   "<userid> - <shipment_id>"
        if valid_sku(json_data.get('variants')[0].get('sku')):
            return json_data.get('variants')[0].get('sku').split('-')[0]
        raise ValueError("JSON sku is not formatted as expected: {}".format(json_data))
