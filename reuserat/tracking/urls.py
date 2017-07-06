# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(regex=r'^schedule_pickup/(?P<next>.+)/$',
        view=views.tracking_schedule_pickup,
        name='track_schedule_pickup'),
]


