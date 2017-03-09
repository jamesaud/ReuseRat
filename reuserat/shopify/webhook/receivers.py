from reuserat.shopify.models import Item,Status,ItemOrderDetails
from reuserat.shipments.models import Shipment
from reuserat.users.models import User
from reuserat.stripe.helpers import create_charge
from ..helpers import valid_sku


'''
RECEIVERS FOR WEBHOOK SIGNALS ARE DEFINED BELOW.
ROUTING IS IN APPS.PY

Improve:
 - create JSON validation templates which we can verify: http://python-jsonschema.readthedocs.io/en/latest/validate/
'''

class AbstractShopifyReceiver:

    @classmethod
    def _get_shopify_json(cls, json_sender_data):
        return json_sender_data['data']  # parse out the sender signal and name



class ProductReceivers(AbstractShopifyReceiver):
    """
    Using Item instead of Product because that's what our Model is called.
    """
    @classmethod
    def item_create(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        shipment = cls._get_shipment(shopify_json)  # Get the related shipment, specified in 'SKU'
        item = Item(data=shopify_json,
                    id=shopify_json['variants'][0]['product_id'],
                    shipment=shipment,
                    handle=shopify_json['handle'],
                    name=shopify_json['title'],
                    is_visible=True if shopify_json['published_at'] else False,
                    )
        item.save()

    @classmethod
    def item_update(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        item = cls._get_item(shopify_json)
        item.data = shopify_json
        item.handle = shopify_json['handle']
        item.name = shopify_json['title']
        item.is_visible= True if shopify_json['published_at'] else False
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
            item = Item.objects.get(pk=json_data['variants'][0]['product_id'])
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
        if valid_sku(json_data.get('variants')[0].get('sku')):
            return json_data.get('variants')[0].get('sku').split('-')[0]
        raise ValueError("JSON sku is not formatted as expected: {}".format(json_data))



class OrderReceivers(AbstractShopifyReceiver):
    """
    This class is responsible for handling order related webhooks from Shopify
    """
    @classmethod
    def order_payment(cls, sender, **kwargs):
        shopify_json  = cls._get_shopify_json(kwargs)
        item_list = shopify_json['line_items']
        for item in item_list:
            # Update the shipment model, decrease the number of items for that shipment,if its 0 delete the shipment
            try:
                item_object = Item.objects.get(pk=item['product_id'])
                item_object.status=Status.SOLD
                # Create an object for ItemOrderDetails
                item_order_details = ItemOrderDetails(order_data=shopify_json, item=item_object)
                user_name = item_object.shipment.user.get_full_name()
                charge_id = create_charge(item_object.shipment.user.stripe_account.account_id,item['price'],user_name)
                item_order_details.charge_id = charge_id

            except Exception as e:
                print(e)
                raise





