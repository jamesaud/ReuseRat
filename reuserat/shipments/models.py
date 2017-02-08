from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from reuserat.users.models import User

class Shipment(models.Model):
    user =  models.ForeignKey(User,
                              on_delete=models.CASCADE)
    name =  models.CharField(max_length=200)
    description =  models.CharField(max_length=1000, blank=False)
    created = models.DateTimeField(auto_now_add=True,)
    modified = models.DateTimeField(auto_now=True,)


