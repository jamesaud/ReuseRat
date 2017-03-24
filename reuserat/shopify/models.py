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
    Represents a physical item that the user has, as well as containing the relevant shopify.com data.
    """
    id = models.CharField(max_length=100, primary_key=True, unique=True)  # Must Be Shopify product ID!!!
    data = JSONField()  # Shopify Json Data
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)  # Shopify  Name
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
    """Contains the shopify details of an item"""
    item = models.OneToOneField(Item, primary_key=True)
    transfer_id = models.CharField(max_length=100)
    order_data = JSONField() # Shopify order data

    def __str__(self):
        return "Order details for: " + str(self.item)


# Store webhook in DB to make sure we don't give the user for hte same webhook twice, if shopify accidentally sends the same webhook.
class Webhook(models.Model):
    webhook_id = models.CharField(max_length=50, primary_key=True)



