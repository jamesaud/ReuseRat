from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from urllib.parse import urljoin
import os
from reuserat.shipments.models import Shipment
from config.settings.common import SHOPIFY_DOMAIN_NAME


class Item(models.Model):

    id = models.CharField(max_length=100, primary_key=True, blank=False, null=False)  # Must Be Shopify product ID!!


    shipment = models.ForeignKey(Shipment,
                                  on_delete=models.CASCADE)

    name =  models.CharField(max_length=200)  # Shopify  Name
    handle = models.CharField(max_length=200)  # Shopify Handle


    def get_shopify_url(self):
        return urljoin("https://www.{}.com".format(SHOPIFY_DOMAIN_NAME), os.path.join('products', self.handle))



