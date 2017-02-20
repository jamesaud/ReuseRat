from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from urllib.parse import urljoin
import os
from reuserat.shipments.models import Shipment
from config.settings.common import SHOPIFY_DOMAIN_NAME
from django.conf import settings
from .helpers import get_shopify_product_url, get_shopify_admin_url


class Item(models.Model):

    id = models.CharField(max_length=100, primary_key=True)  # Must Be Shopify product ID!!


    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)

    name =  models.CharField(max_length=200)  # Shopify Item Name
    handle = models.CharField(max_length=200)  # Shopify Handle
    is_visible = models.BooleanField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_shopify_url(self):
        return get_shopify_product_url(self.handle)

    def get_shopify_admin_url(self):
        return get_shopify_admin_url(self.id)

    def __str__(self):
        return self.name


