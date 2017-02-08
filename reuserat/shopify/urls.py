# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from .views import *

"""
Routing for the individual webooks is in signals.py and handled by the ShopifyWebhookBaseView
"""
urlpatterns = [
    url(
        regex=r'^webhook/$',
        view=ShopifyWebhookBaseView.as_view(),
        name='webhookView'
    ),
]
