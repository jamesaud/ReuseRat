# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse_lazy,reverse
from django.shortcuts import render,render_to_response,redirect
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView,FormView


from .models import Shipment
from django.views.generic.edit import CreateView
from .forms import ShipmentForm
from reuserat.users.models import User


class ShipmentDetailView(LoginRequiredMixin,DetailView):
    model = Shipment
    # These next two lines tell the view to index lookups by username
    # As the shipments are based on the user i.e the seller.
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, **kwargs):
        context = super(ShipmentDetailView, self).get_context_data(**kwargs)
        return context


# Template View
class ShipmentOrderView(LoginRequiredMixin,CreateView):
     model = Shipment
     template_name = 'shipments/shipment_create.html'
     form_class = ShipmentForm

     # Specify the template page where you want to got once it succeeds
     def get_success_url(self):
            return reverse('shipments:shipmentDetail',kwargs={'pk': self.object.id})

     def get_context_data(self,**kwargs):
        context = super(ShipmentOrderView,self).get_context_data(**kwargs)
        return context

     def form_valid(self, form):
        #Automatically saved so the responsiblity of adding user id
        form.instance.user_id=self.request.user.id
        return super(ShipmentOrderView, self).form_valid(form)





