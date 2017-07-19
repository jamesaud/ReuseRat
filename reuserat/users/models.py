# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from localflavor.us import models as usmodels
from reuserat.stripe.models import StripeAccount, PaypalAccount
from reuserat.stripe.helpers import retrieve_balance, cents_to_dollars
from django.core.validators import RegexValidator

class PaymentChoices:
    CHECK = 'Check'
    DIRECT_DEPOSIT = 'Direct Deposit'
    PAYPAL = 'Paypal'
    CHOICES = (
        (CHECK, 'Check'),
        (DIRECT_DEPOSIT, 'Direct Deposit'),
        (PAYPAL, 'Paypal'),
    )

class Address(models.Model):
    address_line = models.CharField(_('Address Line'), max_length=30, blank=False, null=False)
    address_apartment = models.CharField(_('Apartment #'), max_length=30, blank=True, null=True)
    city = models.CharField(_('City'),max_length=50, blank=False, null=False)
    state = usmodels.USStateField(blank=False, null=False)
    zipcode = usmodels.USZipCodeField(max_length=20, blank=False, null=False)
    country = models.CharField(_('Country'), max_length=30, blank=True, null=False, default ="US") #Stripe only accepts US accounts


    def to_html(self):
        apt = "<li>Apartment #{}</li>".format(self.address_apartment) if self.address_apartment else ''
        return\
        """
        <li>{add}</li>
        {apt}
        <li>{city}, {state}, {zip}</li>
        """.format(add=self.address_line, city=self.city, state=self.state, zip=self.zipcode, apt=apt)

    def get_full_address_line(self):
        if self.address_apartment:
            return self.address_line + ", " + self.address_apartment
        return self.address_line

@python_2_unicode_compatible
class User(AbstractUser):
    # Refer to abstract user: https://docs.djangoproject.com/en/1.10/ref/contrib/auth/#django.contrib.auth.models.User
    # First Name and Last Name do not cover name patterns around the globe.
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(_('First Name'), blank=False, null=True, max_length=255)
    last_name = models.CharField(_('Last Name'), blank=False, null=True, max_length=255)
    payment_type = models.CharField(_('Payment Type'), choices=PaymentChoices.CHOICES, max_length=255, blank=False, default="Check")
    phone = usmodels.PhoneNumberField(blank=False, null=True)

    # Payment options
    stripe_account = models.OneToOneField(StripeAccount, on_delete=models.SET_NULL, null=True)
    paypal_account = models.OneToOneField(PaypalAccount, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail')

    def get_current_balance(self):
        # Call function here from helpers
        # External API Call
        return cents_to_dollars(retrieve_balance(self.stripe_account.secret_key))

    def get_primary_email(self):
        return self.emailaddress_set.filter(primary=True).first() or None

    def has_completed_signup(self):
        return True if self.address and self.payment_type else False

    def get_verified_emails(self):
        return self.emailaddress_set.filter(verified=True)

    @property
    def PaymentChoices(self):
        """Allow a views and templates to access payment choices easily."""
        return PaymentChoices
