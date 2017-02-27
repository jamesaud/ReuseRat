from django.db import models

from reuserat.shipments.models import Shipment

from .helpers import get_shopify_product_url, get_shopify_admin_url
from django.contrib.postgres.fields import JSONField


class Item(models.Model):

    """
    Everything in Item is set through the save method through the json data that shopify provides. Only need to provide
    the 'id' and the 'data'.
    """
    data = JSONField() # Shopify Json Data


    id = models.CharField(max_length=100, primary_key=True)  # Must Be Shopify product ID!
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    name =  models.CharField(max_length=200)  # Shopify  Name
    handle = models.CharField(max_length=200)  # Shopify Handle
    is_visible = models.BooleanField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    def get_shopify_url(self):
        return get_shopify_product_url(self.handle)


    def get_shopify_admin_url(self):
        return get_shopify_admin_url(self.id)


    def save(self, override=False, *args, **kwargs):
        """
        :param override: Boolean, allows the user to set their own fields instead of using the JsonData to auto-set.
        """

        if not override:
            self.name = self.data.get('title')
            self.handle = self.data.get('handle')
            self.is_visible = True if self.data.get('published_at') else False

        super(Item, self).save(*args, **kwargs)



    def __str__(self):
        return self.name


