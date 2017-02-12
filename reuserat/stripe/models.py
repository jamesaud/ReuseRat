from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from reuserat.users.models import User


#stripe Managed Accounts required fields.
#These should be hidden from the users as we are managing their stripe accounts(Managed).
class StripeAccount(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)

    stripe_account_id = models.CharField(_('stripe AccountId'), blank=False, null=True, max_length=255)
    stripe_secret_key = models.CharField(_('stripe Secret'), blank=False, null=True, max_length=255)
    stripe_publishable_key = models.CharField(_('stripe Publishable'), blank=False, null=True, max_length=255)

