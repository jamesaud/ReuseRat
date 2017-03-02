from django.db import models
from django.utils.translation import ugettext_lazy as _


# These should be hidden from the users as we are managing their stripe accounts(Managed).

class StripeAccount(models.Model):

    account_id = models.CharField(_('stripe AccountId'), blank=False, max_length=255, primary_key=True) # Stripe account ID

    secret_key = models.CharField(_('stripe Secret'), blank=False, max_length=255)
    publishable_key = models.CharField(_('stripe Publishable'), blank=False, max_length=255)

    account_holder_name = models.CharField(max_length=255)

    account_number_last_four = models.IntegerField()
    account_number_length = models.IntegerField()

    routing_number_last_four = models.IntegerField()


