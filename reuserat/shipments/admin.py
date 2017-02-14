from django.contrib import admin

from reuserat.shopify.api.forms import ShopifyItemRedirectForm
from .models import Shipment


class ShipmentAdmin(admin.ModelAdmin):
    model = Shipment

    readonly_fields = ('user', 'name', 'description')
    list_display = ('id', 'name', 'description', 'user')
    search_fields = ['name', 'description', 'id']

    # Override the changform_view and add custom context to be rendered.
    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        # Instantiate the form with the shipment_id set.
        extra_context['shopify_form'] = ShopifyItemRedirectForm(initial={'shipment_id':object_id})
        return super(ShipmentAdmin, self).changeform_view(request, object_id, form_url='', extra_context=extra_context)



admin.site.register(Shipment, ShipmentAdmin)

