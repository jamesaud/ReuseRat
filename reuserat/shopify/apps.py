from django.apps import AppConfig
import logging
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
        logger.info("START- SIGNALS shopify/apps.py",signals)
        signals.products_create.connect(receivers.ProductReceivers.item_create)
        signals.products_update.connect(receivers.ProductReceivers.item_update_or_create)
        signals.products_delete.connect(receivers.ProductReceivers.item_delete)
        signals.orders_paid.connect(receivers.OrderReceivers.order_payment)

