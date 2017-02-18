# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^~shipmentOrder/$',
        view=views.ShipmentOrderView.as_view(),
        name='shipmentOrder'
    ),
    url(
        regex=r'^(?P<pk>\d+)/$',
        view=views.ShipmentDetailView.as_view(),
        name='shipmentDetail'
    ),
    url(
        regex=r'^~shipmentLabel/(?P<shipment_id>\d+)/$',
        view=views.get_shipment_label,
        name='shipmentLabel'
    ),
    url(
        regex=r'^~shipmentLabelPdf/(?P<shipment_id>\d+)/$',
        view=views.ShipmentPdfView.as_view(),
        name='shipmentPdf'
    ),
    url(
        regex=r'^update/(?P<pk>\d+)/$',
        view=views.ShipmentUpdateView.as_view(),
        name='shipmentUpdate'
    ),
    url(
            regex=r'^delete/(?P<pk>\d+)/$',
            view=views.ShipmentDeleteView.as_view(),
            name='shipmentDelete'
        )
]
