# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from reuserat.address.models import AddressField
from localflavor.us.forms import USZipCodeField
from localflavor.us import models as usmodels
from django.db.models.fields.related import ForeignObject

PAYMENT_CHOICES = (
    ('Check', 'Check'),
    ('Paypal', 'Paypal'),
)

class Address(models.Model):
    address_line = models.CharField(_('Address Line #'), max_length=30, blank=True, null=False)
    address_apartment = models.CharField(_('Apartment #'), max_length=30, blank=True, null=False)
    state = usmodels.USStateField(blank=False, null=False)
    zipcode = usmodels.USZipCodeField(max_length=5)
    country = models.CharField(_('Country'), max_length=30, blank=True, null=True,default ="US") #Stripe only accepts US accounts


@python_2_unicode_compatible
class User(AbstractUser):
    # Refer to abstract user: https://docs.djangoproject.com/en/1.10/ref/contrib/auth/#django.contrib.auth.models.User
    # First Name and Last Name do not cover name patterns around the globe.
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(_('First Name'), blank=False, null=True, max_length=255)
    last_name = models.CharField(_('Last Name'), blank=False, null=True, max_length=255)
    payment_type = models.CharField(_('Payment Type'), choices=PAYMENT_CHOICES, max_length=255, blank=False, default="Check")
    phone = usmodels.PhoneNumberField(blank=False, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

