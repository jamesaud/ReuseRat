# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from localflavor.us import models as usmodels
from reuserat.stripe.models import StripeAccount
from reuserat.stripe.helpers import retrieve_balance
import stripe

PAYMENT_CHOICES = (
    ('Check', 'Check'),
    ('Direct Deposit', 'Direct Deposit'),
    ('Paypal', 'Paypal'),
)

class Address(models.Model):
    address_line = models.CharField(_('Address Line'), max_length=30, blank=False, null=False)
    address_apartment = models.CharField(_('Apartment #'), max_length=30, blank=True, null=True)
    city =models.CharField(_('City'),max_length=50, blank=False, null=False)
    state = usmodels.USStateField(blank=False, null=False)
    zipcode = usmodels.USZipCodeField(max_length=20, blank=False, null=False)
    country = models.CharField(_('Country'), max_length=30, blank=True, null=False, default ="US") #Stripe only accepts US accounts

@python_2_unicode_compatible
class User(AbstractUser):
    # Refer to abstract user: https://docs.djangoproject.com/en/1.10/ref/contrib/auth/#django.contrib.auth.models.User
    # First Name and Last Name do not cover name patterns around the globe.
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    stripe_account = models.OneToOneField(StripeAccount, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(_('First Name'), blank=False, null=True, max_length=255)
    last_name = models.CharField(_('Last Name'), blank=False, null=True, max_length=255)
    payment_type = models.CharField(_('Payment Type'), choices=PAYMENT_CHOICES, max_length=255, blank=False, default="Check")
    phone = usmodels.PhoneNumberField(blank=False, null=True)
    birth_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})


    def get_current_balance(self):
        # Call function here from helpers
        try:
            balance = retrieve_balance(self.stripe_account.secret_key)
        except stripe.error.AuthenticationError:
            balance = "Temporarily Unavailable"
        return float("{:.2f}".format(balance))

    def completed_signup(self):
        return True if self.address and self.payment_type else False
