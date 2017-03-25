from django.db import models
from reuserat.users.models import User

class Shipment(models.Model):
    user =  models.ForeignKey(User,
                              on_delete=models.CASCADE)
    name =  models.CharField(max_length=50)
    description =  models.CharField(max_length=1000, blank=False)
    is_physical = models.BooleanField(default=False)

    tracking_number = models.CharField(max_length=25, null=True, blank=True)  # USPS tracking number
    receipt = models.ImageField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_shipment_sku(self):
        return "{0}-{1}".format(self.user_id, self.id)   # Set the sku to be <userid>-<shipmentid>

    def get_visible_items(self):
        return self.item_set.filter(is_visible=True)

    def has_visible_items(self):
        return any(self.get_visible_items())

    def __str__(self):
        return "Name '{0}' for user '{1}'".format(self.name, str(self.user))

    class Meta:
        ordering = ('modified',)
