from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import Item

class ItemAdmin(admin.ModelAdmin):
    model = Item
    list_display = ('id', 'name', 'handle', 'shipment')
    readonly_fields = ('shipment', 'handle', 'id', 'name')


admin.site.register(Item, ItemAdmin)



