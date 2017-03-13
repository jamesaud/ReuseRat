from django.db import models

from reuserat.shipments.models import Shipment

from .helpers import get_shopify_product_url, get_shopify_admin_url
from django.contrib.postgres.fields import JSONField
from enum import Enum


class Status:
    NOT_SOLD = 'NOT_SOLD'
    SOLD = 'SOLD'

    STATUS_CHOICES = (
        (NOT_SOLD, 'Not Sold'),
        (SOLD, 'Sold'),
    )

class Item(models.Model):

    """
    Everything in Item is set through the save method through the json data that shopify provides. Only need to provide
    the 'id' and the 'data'.
    """
    id = models.CharField(max_length=100, primary_key=True)  # Must Be Shopify product ID!

    data = JSONField()  # Shopify Json Data
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    name =  models.CharField(max_length=200)  # Shopify  Name
    handle = models.CharField(max_length=200)  # Shopify Handle
    is_visible = models.BooleanField()
    status = models.CharField(max_length=100, choices=Status.STATUS_CHOICES, default=Status.NOT_SOLD)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    def get_shopify_url(self):
        return get_shopify_product_url(self.handle)


    def get_shopify_admin_url(self):
        return get_shopify_admin_url(self.id)

    def __str__(self):
        return self.name

    def is_sold(self):
        return self.status == Status.SOLD


class ItemOrderDetails(models.Model):
    # Order ID
    item = models.OneToOneField(Item, primary_key=True)
    charge_id =models.CharField(null=True,max_length=200)
    transfer_id=models.IntegerField(null=True)
    order_data = JSONField(null=True)

    def __str__(self):
        return self.name






