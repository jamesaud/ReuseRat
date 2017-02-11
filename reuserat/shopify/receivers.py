from .models import Item
from reuserat.shipments.models import Shipment
import re

'''
RECEIVERS FOR WEBHOOK SIGNALS ARE DEFINED BELOW.
ROUTING IS IN APPS.PY

Improve:
 - create JSON validation templates which we can verify: http://python-jsonschema.readthedocs.io/en/latest/validate/
'''

def valid_sku(sku):
    if re.findall('[\d]+-[\d]+', sku):
        return True
    return False


class ProductReceivers:

    """
    Using Item instead of Product because that's what our Model is called.
    """

    @classmethod
    def item_create(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)

        shipment = cls._get_shipment(shopify_json)  # Get the related shipment, specified in 'SKU'

        item = cls._create_item(shipment, shopify_json)
        item.save()


    """
    Helper Functions Below
    """
    @classmethod
    def _create_item(cls, shipment, json_data):
        """

        :param shipment: Shipment to add item to.
        :param json_data: Json from shopify
        :return: Item, the item that is created from the json_data (but not saved yet1)
        """
        id, name, handle = json_data.get('id'), json_data.get('title'), json_data.get('handle')
        if name and handle and isinstance(shipment, Shipment):
            return Item(id=id, shipment=shipment, name=name, handle=handle)

        raise ValueError('{0}, are not valid args to be turned into Item from json: {1}'.format([id, name, handle, shipment], json_data))

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
        if cls._validate_json(json_sender_data['data']):
            return json_sender_data['data']  # parse out the sender signal and name


    @staticmethod
    def _validate_json(json_data):
        """
        Checks if the json is in a valid format.
        Requires:
            - sku number with a '-' in between the user_id and shipment_id, like 526635-34
            - proper json formatting
        :param json_data: json from shopify
        :return: Bool, if json meets the valid criteria.
        """
        if len(json_data.get('variants')) >= 1: # Verify there is variants, which contains a list of variants.
            if json_data.get('variants')[0].get('sku'): # Sku is contained in variants. Almost always will get 1 variant.
                sku = json_data.get('variants')[0].get('sku')
                if valid_sku(sku): # Sku should contain 1 dash.
                    return True

        raise ValueError("Json Incorrectly formatted, or 'sku' is incorrectly formattted: {}".format(sku))

    @classmethod
    def _get_shipment_id(cls, json_data):
        # The first variant's SKU, which is the same as all variants SKU.
        # Split on dash because the SKU is entered in as:   "<userid> - <shipment_id>"
        return json_data.get('variants')[0].get('sku').split('-')[1]


    @classmethod
    def _get_user_id(cls, json_data):
        # The first variant's sku, which is the same as all variants sku
        # Split on dash because the SKU is entered in as:   "<userid> - <shipment_id>"
        return json_data.get('variants')[0].get('sku').split('-')[0]

