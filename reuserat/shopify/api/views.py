
from config.settings.common import SHOPIFY_APP_NAME
from django.http.response import HttpResponse

from reuserat.shopify.api.helpers import create_product
from django.contrib.admin.views.decorators import staff_member_required
from reuserat.shipments.models import Shipment
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from .forms import ShopifyItemRedirectForm
from ..helpers import get_shopify_admin_url


@staff_member_required
def create_item(request):
    if request.method == 'POST':
        form = ShopifyItemRedirectForm(request.POST)
        if form.is_valid():
            shipment = get_object_or_404(Shipment, pk=form.cleaned_data.get('shipment_id'))
            sku = shipment.get_shipment_sku()
            print("shopify/api/view.py SKU-",sku)
            try:
                product = create_product(sku=sku, title=form.cleaned_data.get('item_name'))  # Returns a Shopify Product
                product_id = product.id
                return redirect(get_shopify_admin_url(product_id))
            except Exception as e:
                raise Http404("Could not create product: {}".format(e))
        else:
            raise Http404("POST data is invalid: {}".format(request.POST))

    raise Http404("Only POST requests are allowed by adminstrative accounts.")
