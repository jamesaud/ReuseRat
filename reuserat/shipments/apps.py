from django.apps import AppConfig


class ShipmentsConfig(AppConfig):
    name = 'reuserat.shipments'
    verbose_name = "Shipments"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
