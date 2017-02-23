# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),

    url(
        regex=r'^~testCharge/$',
        view=views.testCharge,
        name='testCharge'
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/complete_signup/$',
        view=views.UserCompleteSignupView.as_view(),
        name='complete_signup'
    ),
    url(
        regex=r'^~updatepayment/$',
        view=views.update_payment_information,
        name='update_payment_information'
    ),
]
