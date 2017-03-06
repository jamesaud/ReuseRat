from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
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
