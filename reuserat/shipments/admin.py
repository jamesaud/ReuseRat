

from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import Shipment
from reuserat.shopify.models import Item
from django import forms
import reuserat.shopify.api.helpers as shop


class ItemInline(admin.StackedInline):
    model = Item
    readonly_fields = ('shipment', 'name', 'handle', 'id')



class AddShopifyItemForm(forms.ModelForm):
    new_item = forms.CharField(label="Add New Item", required=False)


    def save(self, commit=True):
        new_item = self.cleaned_data.get('new_item', None)
        if new_item:
            user = self.cleaned_data
            print(user)
            #shop.create_product()
        return super(AddShopifyItemForm, self).save(commit=commit)


    class Meta:
        model = Shipment
        fields = ['id', 'name', 'description', 'user']



class ShipmentAdmin(admin.ModelAdmin):
    model = Shipment
    form = AddShopifyItemForm


    readonly_fields = ('user', 'name', 'description')
    list_display = ('id', 'name', 'description', 'user')
    search_fields = ['name', 'description', 'id']


admin.site.register(Shipment, ShipmentAdmin)

