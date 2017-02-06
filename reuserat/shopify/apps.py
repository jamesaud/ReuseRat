from django.apps import AppConfig


class ShopifyConfig(AppConfig):
    name = 'reuserat.shopify'
    verbose_name = "Shopify"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
