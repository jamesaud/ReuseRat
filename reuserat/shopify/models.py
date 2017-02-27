from django.db import models

from reuserat.shipments.models import Shipment

from .helpers import get_shopify_product_url, get_shopify_admin_url
from django.contrib.postgres.fields import JSONField


class Item(models.Model):

    id = models.CharField(max_length=100, primary_key=True)  # Must Be Shopify product ID!!


    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)

    name =  models.CharField(max_length=200)  # Shopify  Name
    handle = models.CharField(max_length=200)  # Shopify Handle
    is_visible = models.BooleanField()

    data = JSONField() # Shopify Json Data

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_shopify_url(self):
        return get_shopify_product_url(self.handle)

    def get_shopify_admin_url(self):
        return get_shopify_admin_url(self.id)

    def __str__(self):
        return self.name


