
from config.settings.common import SHOPIFY_APP_NAME
from django.http.response import HttpResponse

from reuserat.shopify.api.helpers import create_product
from django.contrib.admin.views.decorators import staff_member_required
from reuserat.shipments.models import Shipment
from django.shortcuts import get_object_or_404
from django.http import Http404
from .forms import ShopifyItemRedirectForm


def shopify_test(request):

    new_product = create_product(sku='12-32', title='My Product')
    return HttpResponse("created")



@staff_member_required
def create_item(request):
    if request.method == 'POST':
        form = ShopifyItemRedirectForm(request.POST)
        if form.is_valid():
            shipment = get_object_or_404(Shipment, pk=form.cleaned_data.get('shipment_id'))
            sku = shipment.get_shipment_sku()
            try:
                product = create_product(sku=sku, title=form.cleaned_data.get('item_name'))
            except Exception as e:
                raise Http404("Could not create product: {}".format(e))

            return HttpResponse('Successfully Created Item')

    raise Http404("Only POST reqeusts are allowed.")
