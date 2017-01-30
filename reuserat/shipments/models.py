from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _



class Shipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Shipment ID number
    # Shipment status

"""
A shipment can have multiple items in it.
"""
class Item(models.Model):
    #name = models.Char
    # 
    pass