from django.conf.urls import url
from django.views.generic import TemplateView, RedirectView
from . import views
from django.shortcuts import reverse

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='knowledge:questions', permanent=True)),

    url(r'^shipping-guide/$',
            TemplateView.as_view(template_name='knowledge/shipping.html'),
            name='shipping'),

        url(r'^shipping-calculator/$',
            TemplateView.as_view(template_name='knowledge/shipping_calculator.html'),
            name='shipping_calculator'),

        url(r'^quickstart/$',
            TemplateView.as_view(template_name='knowledge/quickstart.html'),
            name='quickstart'),

        url(r'^common-questions/$',
            views.faq_view,
            name='questions'),

        url(r'^payment-information/$',
            TemplateView.as_view(template_name='knowledge/payment.html'),
            name='payment'),
]
