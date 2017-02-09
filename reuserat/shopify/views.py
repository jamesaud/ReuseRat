from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import SuspiciousOperation

import json

from .decorators import webhook, app_proxy
from .helpers import get_signal_name_for_topic
from .models import Item
from reuserat.shipments.models import Shipment

from . import signals


import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(webhook, name='dispatch')
class ShopifyWebhookBaseView(View):

    """
    A view to be used as the endpoint for webhook requests from Shopify.
    Inherit from this view to aquire the json_data variable, set with POST.
    Override the "post" method, call "super" as the first piece of code - example in the ShopifyProductCreateView
    Accepts only the POST method and utilises the @webhook view decorator to validate the request.

    """

    json_data = {}


    def post(self, request, *args, **kwargs):
        """
        Receive a webhook POST request.
        The reason we use "raise" is to prevent the overrided classes from having to check the status code that is returned.
        When inherriting it isn't necessary to check the status code, as only a 200 status can pass through.
        """

        # Convert the topic to a signal name and trigger it.
        signal_name = get_signal_name_for_topic(request.webhook_topic)
        try:
            signals.webhook_received.send_robust(self, domain = request.webhook_domain, topic = request.webhook_topic, data = request.webhook_data)
            getattr(signals, signal_name).send_robust(self, domain = request.webhook_domain, topic = request.webhook_topic, data = request.webhook_data)
        except AttributeError as e:
            logger.error("Encountered Shopify Webhook Signal Error: {0}".format(e))
            raise SuspiciousOperation


        return HttpResponse("Ok") #200 response code




class LiquidTemplateView(TemplateView):
    """
    A view extending Django's base TemplateView that provides conveniences for returning a
    liquid-templated view from an app proxy request.
    """

    content_type = getattr(settings, 'LIQUID_TEMPLATE_CONTENT_TYPE', 'application/liquid; charset=utf-8')

    @method_decorator(app_proxy)
    def dispatch(self, request, *args, **kwargs):
        return super(LiquidTemplateView, self).dispatch(request, *args, **kwargs)




'''
RECEIVERS FOR WEBHOOK SIGNALS ARE DEFINED BELOW.
ROUTING IS IN APPS.PY

Improve:
 - create JSON validation templates which we can verify: http://python-jsonschema.readthedocs.io/en/latest/validate/
'''

class ProductReceivers:

    """
    Using Item instead of Product because that's what our Model is called. A Shipment can have many Items.

    """

    @classmethod
    def item_create(cls, sender, **kwargs):
        shopify_json = cls._get_shopify_json(kwargs)
        shipment = cls._get_shipment(shopify_json)  # Get the related shipment, specified in 'SKU'

        item = cls._create_item(shipment, shopify_json)
        item.save()

        #print(item)
        #print(item.id)

    """
    Helper Functions Below
    """
    @classmethod
    def _create_item(cls, shipment, json_data):
        """

        :param shipment: Shipment to add item to.
        :param json_data: Json from shopify
        :return: Item, the item that is created from the json_data (but not saved yet1)
        """
        id, name, handle = json_data.get('id'), json_data.get('title'), json_data.get('handle')
        if name and handle and isinstance(shipment, Shipment):
            return Item(id=id, shipment=shipment, name=name, handle=handle)

        raise ValueError('{0}, are not valid args to be turned into Item from json: {1}'.format([id, name, handle, shipment], json_data))

    @classmethod
    def _get_shipment(cls, json_data):
        try:
            id = cls._get_shipment_id(json_data)
            return Shipment.objects.get(pk=cls._get_shipment_id(json_data))
        except Shipment.DoesNotExist:
            print("Shipment with ID: " + str(id) + "  does not exist in database from json_data: {}".format(json_data))
            raise


    @staticmethod
    def _get_shopify_json(json_sender_data):
        return json_sender_data['data']  # parse out the sender signal and name


    @staticmethod
    def _valid_json(json_data):
        """
        Checks if the json is in a valid format.
        Requires:
            - sku number with a '-' in between the user_id and shipment_id, like 526635-34
            - proper json formatting
        :param json_data: json from shopify
        :return: Bool, if json meets the valid criteria.
        """
        if len(json_data.get('variants')) >= 1: # Verify there is variants, which contains a list of variants.
            if json_data.get('variants')[0].get('sku'): # Sku is contained in variants. Almost always will get 1 variant.
                if len(json_data.get('variants')[0].get('sku').split('-')) == 2: # Sku should contain 1 dash.
                    return True

        return False

    @classmethod
    def _get_shipment_id(cls, json_data):
        # The first variant's SKU, which is the same as all variants SKU.
        # Split on dash because the SKU is entered in as:   "<userid> - <shipment_id>"
        if cls._valid_json(json_data):
            return json_data.get('variants')[0].get('sku').split('-')[1]

        raise TypeError("Json not as expected. Missing 'variants' or 'sku' is missing a dash")

    @classmethod
    def _get_user_id(cls, json_data):
        # The first variant's sku, which is the same as all variants sku
        # Split on dash because the SKU is entered in as:   "<userid> - <shipment_id>"
        if cls._valid_json(json_data):
            return json_data.get('variants')[0].get('sku').split('-')[0]

        raise TypeError("Json not as expected. Missing 'variants' or 'sku' is missing a dash")

