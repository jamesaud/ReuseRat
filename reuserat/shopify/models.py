from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from urllib.parse import urljoin
import os
from reuserat.shipments.models import Shipment
from config.settings.common import SHOPIFY_DOMAIN_NAME


class Item(models.Model):
    shipment = models.ForeignKey(Shipment,
                                  on_delete=models.CASCADE)

    id = models.CharField(max_length=100, primary_key=True)  # Shopify product ID
    name =  models.CharField(max_length=200)  # Shopify Item Name
    handle = models.CharField(max_length=200)  # Shopify Handle


    def get_shopify_url(self):
        return urljoin(SHOPIFY_DOMAIN_NAME, os.path.join('products', self.handle))



