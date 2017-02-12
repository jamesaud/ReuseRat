from django.apps import AppConfig

from django.core.signals import request_finished
from django.dispatch import receiver

class ShopifyConfig(AppConfig):
    name = 'reuserat.shopify'
    verbose_name = "Shopify"

    def ready(self):
        """
            Override this to put in:
            Users system checks
            Users signal registration
        """
        from . import signals, receivers

        signals.products_create.connect(receivers.ProductReceivers.item_create)
        signals.products_update.connect(receivers.ProductReceivers.item_update)
        signals.products_delete.connect(receivers.ProductReceivers.item_delete)
