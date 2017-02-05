from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import Shipment

class ShipmentAdmin(admin.ModelAdmin):
    model = Shipment
    

admin.site.register(Shipment, ShipmentAdmin)