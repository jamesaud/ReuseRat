from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import Item, ItemOrderDetails

class ItemOrderDetailsAdmin(admin.ModelAdmin):
    model = ItemOrderDetails

class ItemAdmin(admin.ModelAdmin):
    model = Item
    list_display = ('id', 'name', 'handle', 'shipment', 'is_visible', 'created', 'modified')
    #readonly_fields = ('shipment', 'handle', 'id', 'name', 'is_visible', 'data', 'created', 'modified')



admin.site.register(Item, ItemAdmin)
admin.site.register(ItemOrderDetails, ItemOrderDetailsAdmin)





