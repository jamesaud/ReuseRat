from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
        url(r'^shipping-guide/$', 
            TemplateView.as_view(template_name='knowledge/shipping.html'), 
            name='shipping'),
        url(r'^quickstart/$', 
            TemplateView.as_view(template_name='knowledge/quickstart.html'), 
            name='quickstart'),
        url(r'^common-questions/$', 
            TemplateView.as_view(template_name='knowledge/questions.html'), 
            name='questions'),
        url(r'^payment-information/$', 
            TemplateView.as_view(template_name='knowledge/payment.html'), 
            name='payment'),
        
]
