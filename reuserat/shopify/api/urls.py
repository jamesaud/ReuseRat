# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(regex=r'^test/$',
        view=views.shopify_test,
        name='shopifytest'
        ),
    url(regex=r'^create_item/$',
        view=views.create_item,
        name='create_item'
        ),
]

