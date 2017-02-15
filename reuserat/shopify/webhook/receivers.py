from reuserat.shopify.models import Item
from reuserat.shipments.models import Shipment
from ..helpers import valid_sku

'''
RECEIVERS FOR WEBHOOK SIGNALS ARE DEFINED BELOW.
ROUTING IS IN APPS.PY

Improve:
 - create JSON validation templates which we can verify: http://python-jsonschema.readthedocs.io/en/latest/validate/
'''


class ProductReceivers:

    """
    Using Item instead of Product because that's what our Model is called.
    """

    @classmethod
    def item_create(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        shipment = cls._get_shipment(shopify_json)  # Get the related shipment, specified in 'SKU'
        cls._create_item(shopify_json, shipment)


    @classmethod
    def item_update(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        cls._update_item(shopify_json)


    @classmethod
    def item_delete(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        cls._delete_item(shopify_json)

    """
    Helper Functions Below
    """

    @classmethod
    def _create_item(cls, json_data, shipment=None):
        """

        :param shipment: Shipment to add item to.
        :param json_data: Json from shopify
        :return: Item, the item that is created from the json_data
        """
        id, name, handle, is_visible = json_data.get('id'), json_data.get('title'), json_data.get('handle'), \
                                        json_data.get('published_at', 'DNE')

        # visibility is None if not published, so we set up another variable to see if the call failed.
        if name and handle and isinstance(shipment, Shipment) and (is_visible != 'DNE'):
            item = Item(id=id, shipment=shipment, name=name, handle=handle, is_visible=True if is_visible else False)
            item.save()
            return item
        raise ValueError('{0}, are not valid args to be turned into Item from json: {1}'.format([id, name, handle, shipment], json_data))

    @classmethod
    def _get_item(self, json_data):
        try:
            item = Item.objects.get(pk=json_data['id'])
        except Item.DoesNotExist:
            print("Getting item using primary key found from 'id' in json does not exist: {}".format(json_data))
            raise
        return item

    @classmethod
    def _update_item(cls, json_data):
        """

        :param shipment: Shipment to add item to.
        :param json_data: Json from shopify
        :return: Item, the item that is created from the json_data (but not saved yet1)
        """
        id, name, handle, is_visible = json_data.get('id'), json_data.get('title'), json_data.get('handle'), \
                                       json_data.get('published_at', 'DNE')
        item = cls._get_item(json_data)

        if name and handle and (is_visible != 'DNE'):
            item.handle = handle
            item.name = name
            item.is_visible = True if is_visible else False   # False if is_is_visible is None, else True
            item.save()
            return item
        raise ValueError("Json misisng name or handle: ".format(json_data))

    @classmethod
    def _delete_item(cls, json_data):
        item = cls._get_item(json_data)
        item.delete()
        return True

    @classmethod
    def _get_shipment(cls, json_data):
        try:
            id = cls._get_shipment_id(json_data)
            return Shipment.objects.get(pk=id)
        except Shipment.DoesNotExist:
            print("Shipment with ID + does not exist in database from json_data: {}".format(json_data))
            raise


    @classmethod
    def _get_shopify_json(cls, json_sender_data):
        return json_sender_data['data']  # parse out the sender signal and name


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
