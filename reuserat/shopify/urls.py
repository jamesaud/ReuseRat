# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from .views import WebhookView


urlpatterns = [
    url(
        regex=r'^$',
        view=WebhookView.as_view(),
        name='webhookView'
    ),
]
