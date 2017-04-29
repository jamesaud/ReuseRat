from django.conf.urls import patterns, url

from reuserat.shopify.webhook.views import WebhookView

urlpatterns = patterns('',
                       url(r'webhook/', WebhookView.as_view(), name='webhook'),
                       )
