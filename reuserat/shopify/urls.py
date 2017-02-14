# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include

from reuserat.shopify.webhook.views import *
from .api import urls as api_urls

"""
Routing for the individual webooks is in signals.py and handled by the ShopifyWebhookBaseView
"""
urlpatterns = [
    url(
        regex=r'^webhook/$',
        view=ShopifyWebhookBaseView.as_view(),
        name='webhookView'
    ),
    url(r'^api/', include(api_urls, namespace='api')),

]
