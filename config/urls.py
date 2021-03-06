# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^dashboard/', include('reuserat.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Shipments
    url(r'^shipments/', include('reuserat.shipments.urls', namespace='shipments')),

    # Shopify
    url(r'^shopify/', include('reuserat.shopify.urls', namespace='shopify')),

    # Knowledge Base
    url(r'^knowledge/', include('reuserat.knowledge.urls', namespace='knowledge')),

    # Third Party tracking, analytics, & more
    url(r'^tp/', include('reuserat.third_party.urls', namespace='third_party')),

                  # Pickup Page
    url(r'^pickup/', TemplateView.as_view(template_name='pages/pickup.html'), name='pickup'),
    url(r'^privacy-policy/', TemplateView.as_view(template_name='pages/privacypolicy.htm'), name='privacy-policy'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),

        # Custom test URLs
        url(r'^test/$', TemplateView.as_view(template_name='test.html'), name='test'),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
