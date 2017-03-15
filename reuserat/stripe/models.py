from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator


# Docs for EmailAddress at: #https://github.com/pennersr/django-allauth/blob/master/allauth/account/models.py
from allauth.account.models import EmailAddress

# These should be hidden from the users as we are managing their stripe accounts(Managed).

FOUR_DIGIT_VALIDATOR = RegexValidator(regex='^\d{4}$', message='Has to be 4 integers', code='nomatch')

class StripeAccount(models.Model):

    account_id = models.CharField(_('stripe AccountId'), blank=False, max_length=255, primary_key=True) # Stripe account ID
    secret_key = models.CharField(_('stripe Secret'), blank=False, max_length=255)
    publishable_key = models.CharField(_('stripe Publishable'), blank=False, max_length=255)

    # This is the bank account information.
    account_holder_name = models.CharField(max_length=255, null=True, blank=False)
    account_number_last_four = models.CharField(validators=[FOUR_DIGIT_VALIDATOR], max_length=4, null=True, blank=False)
    account_number_length = models.IntegerField(null=True, blank=False)
    routing_number_last_four = models.CharField(validators=[FOUR_DIGIT_VALIDATOR], max_length=4, null=True, blank=False)
    # Length of routing number is 9 digits per USA banking regulations.

    def has_bank(self):
        return True if (self.routing_number_last_four and self.account_number_last_four) else False


class PaypalAccount(models.Model):
    email = models.OneToOneField(EmailAddress)


class Transaction(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    payment_type = models.CharField(_('Payment Type'), max_length=255)
    amount_paid = models.FloatField() # In dollars
    message = models.CharField(max_length=500, null=True, blank=True)


