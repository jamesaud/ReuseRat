from django.contrib import admin

from reuserat.shopify.api.forms import ShopifyItemRedirectForm
from .models import Shipment
from reuserat.shopify.models import Item
from django.utils.html import format_html_join, format_html

class ShipmentAdmin(admin.ModelAdmin):
    model = Shipment

    list_display = ('name', 'description', 'user', 'id')
    search_fields = ['name', 'description', 'id']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_physical:  # Test object exists
            readonly_fields = ('get_items',)

        else:
            readonly_fields = ('user', 'name', 'description', 'get_items', 'is_physical')


        return readonly_fields


    # Override the changform_view and add custom context to be rendered.
    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        if object_id: # Ensures that this is the shipment detail request, not a create shipment request
            extra_context = extra_context or {}

            # Instantiate the form with the shipment_id set.
            extra_context['shopify_form'] = ShopifyItemRedirectForm(initial={'shipment_id': object_id})

        return super(ShipmentAdmin, self).changeform_view(request, object_id, form_url='', extra_context=extra_context)


    def get_items(self, obj):
        wrapper_html = """
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Visible</th>
                <th></th>
            </tr>
            {}
        </table>"""

        # 0: id, 1: name, 2:visibility, 3:url
        inner_template_html = """
        <tr>
            <td>
                {0}
            </td>
            <td>
                {1}
            </td>
            <td>
                {2}
            </td>
            <td>
               <a href='{3}' target='_blank'>Edit On Shopify</a>
            </td>
        </tr>"""

        # Each tuple in the args_generator (list of tuples) gets formatted in the html.
        inner_html = format_html_join(
            sep='\n',
            format_string=inner_template_html,
            args_generator=((item.id, item.name, item.is_visible, item.get_shopify_admin_url()) for item in obj.item_set.all())
        )

        return format_html(wrapper_html, inner_html)  # Works the same as str.format() and also escapes html

    get_items.short_description = 'Items'


admin.site.register(Shipment, ShipmentAdmin)

