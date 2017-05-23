from reuserat.shopify.models import Item, Status, ItemOrderDetails, Webhook
from reuserat.shipments.models import Shipment
from reuserat.users.models import User
from reuserat.stripe.models import Transaction, TransactionPaymentTypeChoices, TransactionTypeChoices
from reuserat.stripe.helpers import create_transfer_to_customer, cents_to_dollars, dollars_to_cents
from django.conf import settings

from stripe.error import StripeError

from ..helpers import valid_sku

'''
RECEIVERS FOR WEBHOOK SIGNALS ARE DEFINED BELOW.
ROUTING IS IN APPS.PY

Improve:
 - create JSON validation templates which we can verify: http://python-jsonschema.readthedocs.io/en/latest/validate/
'''

import logging
logger = logging.getLogger(__name__)


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
        print("SHOPIFY JSONNN IN webhook/receivers.py",shopify_json)
        shipment = cls._get_shipment(shopify_json)  # Get the related shipment, specified in 'SKU'
        print("underneath the RISING SUN")
        item = Item(data=shopify_json,
                    id=shopify_json['variants'][0]['product_id'],
                    shipment=shipment,
                    handle=shopify_json['handle'],
                    name=shopify_json['title'],
                    is_visible=True if shopify_json['published_at'] else False,
                    )
        print(item)
        item.save()

    @classmethod
    def item_update(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        item = cls._get_item(shopify_json)
        item.data = shopify_json
        item.handle = shopify_json['handle']
        item.name = shopify_json['title']
        item.is_visible = True if shopify_json['published_at'] else False
        item.save()

    @classmethod
    def item_update_or_create(cls, sender, **kwargs):
        try:
            cls.item_update(sender, **kwargs)
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
            logger.error("Getting item using primary key found from 'id' in json does not exist: {}".format(json_data))
            raise
        return item

    @classmethod
    def _get_shipment(cls, json_data):
        try:
            id = cls._get_shipment_id(json_data)
            return Shipment.objects.get(pk=id)
        except Shipment.DoesNotExist:
            logger.error("Shipment with ID + does not exist in database from json_data: {}".format(json_data))
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
        shopify_json = cls._get_shopify_json(kwargs)
        item_list = shopify_json['line_items']

        # Guarantee a webhook isn't repeated. Error is raised if it already exists.
        try:
            Webhook.objects.get(webhook_id=shopify_json['id'])
        except Webhook.DoesNotExist:
            webhook = Webhook(webhook_id=shopify_json['id'])
            webhook.save()
        else:
            logger.error("WEBHOOK Already Exists! This is a duplicate! {}".format(shopify_json))
            raise Exception("WEBHOOK Already Exists! This is a duplicate! {}".format(shopify_json))

        for item in item_list:
            try:
                # Update the shipment model
                # Update the status of the item to Sold
                item_object = Item.objects.get(pk=item['product_id'])
            except Item.DoesNotExist as e:
                # This could happen if we add items manually to Shopify that don't belong to users. In that case, it is okay skip over.
                # However, we should log the occurences to make sure nothing is wrong.
                logger.error("FAILED TO GET ITEM {0} FROM DATABASE. | Shopify Json: {1} | Error {2}".format(item, shopify_json, e))
            else:
                item_object.status = Status.SOLD
                user = item_object.shipment.user
                # Create transfer, give the user a their cut of the sale.
                item_price = dollars_to_cents(float(item['price'])) # Stripe takes cents!
                try:
                    amount_cents_for_user = int(item_price * settings.SPLIT_PERCENT_PER_SALE)  # Give the user 50%. If we do referrals, we can give more money to the associated referring user here.
                    transfer_id = create_transfer_to_customer(account_id=user.stripe_account.account_id,
                                                              balance_in_cents=amount_cents_for_user,
                                                              description='{0} Sold Item {1}'.format(user.get_full_name(), item_object.name))
                except StripeError as e:
                    logger.error("FAILED TO CREATE CHARGE FOR ITEM: {0} | Shopify Json: {1} | Error: {2} | User: {3}".format(item, shopify_json, e, user.get_full_name()))
                    raise
                else:

                    transaction = Transaction(user=user,
                                              payment_type=TransactionPaymentTypeChoices.ITEM_SOLD,
                                              amount=cents_to_dollars(amount_cents_for_user),
                                              type=TransactionTypeChoices.IN,
                                              message='Paid for selling the item: ' + item_object.name)
                    # Update the charge id of the item ,for future reference
                    # Save updated objects
                    item_object.save()
                    transaction.save()
                    item_order_details = ItemOrderDetails(order_data=shopify_json, item=item_object, transfer_id=transfer_id)
                    item_order_details.save()

