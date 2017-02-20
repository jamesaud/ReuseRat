from django.apps import AppConfig


class AddressConfig(AppConfig):
    name = 'reuserat.address'
    verbose_name = "Addresses"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
