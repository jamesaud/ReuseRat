from django.apps import AppConfig


class StripeConfig(AppConfig):
    name = 'reuserat.stripe'
    verbose_name = "stripe"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
