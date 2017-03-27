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


"""
It's important to understand how our stripe platform works.
Every transaction is through ACH, whether it's a transfer from our platform account to a connect account, or vice versa.
We don't want this to be under the 'card' source_type, but under 'bank_account' source_type. Stripe has multiple 'source_type' options for a 'Balance' object.
Docs: https://stripe.com/docs/api#balance
So in order to make sure everything transfers the right way, it's also important to make sure that our tests are checking the 'bank_account' balance of a user.
"""
