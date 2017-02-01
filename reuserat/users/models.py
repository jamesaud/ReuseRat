# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from reuserat.address.models import AddressField

PAYMENT_CHOICES = (
    ('Check', 'Check'),
    ('Paypayl', 'Paypal'),
)

def phone_validator(value):
    return RegexValidator(regex=r'^\+?1?\d{9,15}$',
                          message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


@python_2_unicode_compatible
class User(AbstractUser):
    # Refer to abstract user: https://docs.djangoproject.com/en/1.10/ref/contrib/auth/#django.contrib.auth.models.User
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    payment_type = models.CharField(_('Payment Type'), choices=PAYMENT_CHOICES, max_length=255, blank=True)
    phone = models.CharField(validators=[phone_validator], max_length=15, blank=True)
    address = AddressField(related_name='+', blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

