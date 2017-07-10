# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^thanks-for-booking-boxes/$',
        view=views.thank_you_for_booking_boxes,
        name='thanks-for-booking-boxes'
    ),
    url(
        regex=r'^thanks-for-booking-pickup/$',
        view=views.thank_you_for_booking_pickup,
        name='thanks-for-booking-pickup'
    ),
]
