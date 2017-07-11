from django.apps import AppConfig
import logging
from config.logging import setup_logger

setup_logger()
logger = logging.getLogger(__name__)



class ShopifyConfig(AppConfig):
    name = 'reuserat.shopify'
    verbose_name = "Shopify"

    def ready(self):
        """
            Override this to put in:
            Users system checks
            Users signal registration
        """
        from reuserat.shopify.webhook import signals
        from reuserat.shopify.webhook import receivers
        print("STARTING - SIGNALS shopify/apps.py")

        signals.products_create.connect(receivers.ProductReceivers.item_create)
        signals.products_update.connect(receivers.ProductReceivers.item_update_or_create)
        signals.products_delete.connect(receivers.ProductReceivers.item_delete)
        signals.fulfillments_create.connect(receivers.FulfillmentReceivers.fulfillment_create)
