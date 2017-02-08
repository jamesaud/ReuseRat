from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import Item

class ItemAdmin(admin.ModelAdmin):
    model = Item


admin.site.register(Item, ItemAdmin)
