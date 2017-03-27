# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),
    url(
        regex=r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
    url(
        regex=r'^~cashout/$',
        view=views.CashOutView.as_view(),
        name='cash_out'
    ),
    url(

        regex=r'^~complete_signup/$',
        view=views.UserCompleteSignupView.as_view(),
        name='complete_signup'
    ),
    url(
        regex=r'^~updatepayment/$',
        view=views.UpdatePaymentInformation.as_view(),
        name='update_payment_information'
    ),
    url(
        regex=r'^~transactions/$',
        view=views.TransactionListView.as_view(),
        name='transactions'
    ),
]
