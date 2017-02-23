from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
        url(r'^shipping-guide/$', 
            TemplateView.as_view(template_name='knowledge/shipping.html'), 
            name='shipping'),

        url(r'^quickstart/$', 
            TemplateView.as_view(template_name='knowledge/quickstart.html'), 
            name='quickstart'),
]
