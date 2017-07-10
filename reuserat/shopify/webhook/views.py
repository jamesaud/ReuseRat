import logging

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView

from reuserat.shopify.webhook import signals
from .decorators import webhook, app_proxy
from .helpers import get_signal_name_for_topic
from config.logging import setup_logger

setup_logger()
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

    def post(self, request, *args, **kwargs):
        """
        Receive a webhook POST request.
        The reason we use "raise" is to prevent the overrided classes from having to check the status code that is returned.
        When inheriting it isn't necessary to check the status code, as only a 200 status can pass through.
        """
        print("I AM HERE INSIDE SHOPIFY")
        # Convert the topic to a signal name and trigger it.
        signal_name = get_signal_name_for_topic(request.webhook_topic)
        try:
            signals.webhook_received.send_robust(self, domain = request.webhook_domain, topic = request.webhook_topic, data = request.webhook_data)
            getattr(signals, signal_name).send_robust(self, domain = request.webhook_domain, topic = request.webhook_topic, data = request.webhook_data)
            print("SINGAL NAME - WEBHOOK.VIEWS.PY", signal_name)

        except AttributeError as e:
            logger.error("Encountered Shopify Webhook Signal Error: {0}".format(e), exc_info=True)
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




