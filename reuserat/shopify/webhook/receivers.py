from reuserat.shopify.models import Item, Status, ItemOrderDetails
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
from config.logging import setup_logger

setup_logger()
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
        shipment = cls._get_shipment(shopify_json)  # Get the related shipment, specified in 'SKU'
        item = Item(data=shopify_json,
                    id=shopify_json['variants'][0]['product_id'],
                    shipment=shipment,
                    handle=shopify_json['handle'],
                    name=shopify_json['title'],
                    is_visible=False,  # Is set to visible when visible in shopify store
                    )
        item.save()

    @classmethod
    def item_update(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        item = cls._get_item(shopify_json)
        item.data = shopify_json
        item.handle = shopify_json['handle']
        item.name = shopify_json['title']
        item.is_visible = True if shopify_json['id'] else False
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
        try:
            item = Item.objects.get(pk=shopify_json['id'])
        except Exception as e:
            logger.error("Item does not exist while trying to delete")
        else:
            item.delete()




    """
    Helper Functions Below
    """

    @classmethod
    def _get_item(self, json_data):
        try:
            print(" get otem JSON DATA _get_item receviers.py",type(json_data['variants'][0]['product_id']))

            item = Item.objects.get(pk=json_data['variants'][0]['product_id'])
        except Item.DoesNotExist:
            logger.error("Getting item using primary key found from 'id' in json does not exist: {}".format(json_data), exc_info=True)
            raise
        return item

    @classmethod
    def _get_shipment(cls, json_data):
        try:
            id = cls._get_shipment_id(json_data)
            return Shipment.objects.get(pk=id)
        except Shipment.DoesNotExist:
            logger.error("Shipment with ID + does not exist in database from json_data: {}".format(json_data), exc_info=True)
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



class FulfillmentReceivers(AbstractShopifyReceiver):
    """
    This class is responsible for handling Fulfillment related webhooks
    """

    @classmethod
    def _item_already_paid(cls, item):
        """
        We need to make sure not to pay a user twice if we get a webhook twice with the same item.
        :type item: Item
        """
        return True if item.status == Status.SOLD else False

    @classmethod
    def _update_item_status(cls, item):
        """
        Update the item after it's purchased.
        :type item: Item
        """
        item.status = Status.SOLD
        item.save()

    @classmethod
    def _create_transaction(cls, item, user, amount_in_cents):
        transaction = Transaction(user=user,
                                  payment_type=TransactionPaymentTypeChoices.ITEM_SOLD,
                                  amount=cents_to_dollars(amount_in_cents),
                                  type=TransactionTypeChoices.IN,
                                  message='Paid for selling the item: ' + item.name)
        transaction.save()

    @classmethod
    def _create_item_order_details(self, item, transfer_id, shopify_json):
        item_order_details = ItemOrderDetails(order_data=shopify_json, item=item,
                                              transfer_id=transfer_id)
        item_order_details.save()

    @classmethod
    def fulfillment_create(cls, sender, **kwargs):
        logger.error("Fulfillment Triggered")

        shopify_json = cls._get_shopify_json(kwargs)

        logger.error("shopify json Triggered")

        item_list = shopify_json['line_items']
        # Guarantee a webhook isn't repeated. Error is raised if it already exists.

        logger.error("item list Triggered")


        for item in item_list:
            logger.error("Trying to fulfill item: {}".format(item))
            try:
                item_object = Item.objects.get(pk=item['product_id'])
            except Item.DoesNotExist as e:
                # This could happen if we add items manually to Shopify that don't belong to users. In that case, it is okay skip over.
                # However, we should log the occurences to make sure nothing is wrong.
                logger.error(
                    "FAILED TO GET ITEM {0} FROM DATABASE. | Shopify Json: {1} | Error {2}".format(item, shopify_json,
                                                                                                   e), exc_info=True)
            else:
                # The user was already paid for the item, so skip to the next item
                if cls._item_already_paid(item_object):
                    logger.error("Item already paid for, received fulfillment webhook trying to pay again for item: {0} | {1}"\
                                   .format(item, shopify_json))
                    continue


                # Else, pay the user
                user = item_object.shipment.user
                # Create transfer, give the user a their cut of the sale.
                item_price = dollars_to_cents(float(item['price']))  # Stripe takes cents!
                try:
                    amount_cents_for_user = int(item_price * settings.SPLIT_PERCENT_PER_SALE)  # Give the user 50%. If we do referrals, we can give more money to the associated referring user here.
                    logger.error("CREATING TRANSFER TO CUSTOMER")
                    transfer_id = create_transfer_to_customer(account_id=user.stripe_account.account_id,
                                                              balance_in_cents=amount_cents_for_user,
                                                              description='{0} Sold Item {1}'.format(
                                                                  user.get_full_name(), item_object.name))
                except StripeError as e:
                    logger.error(
                        "FAILED TO CREATE CHARGE FOR ITEM: {0} | Shopify Json: {1} | Error: {2} | User: {3}".format(
                            item, shopify_json, e, user.get_full_name()), exc_info=True)
                    raise
                else:
                    logger.error("Creating transaction information")
                    cls._create_transaction(item_object, user, amount_cents_for_user)
                    cls._update_item_status(item_object)
                    cls._create_item_order_details(item_object, transfer_id, shopify_json)

