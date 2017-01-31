# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render,render_to_response,redirect
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView,FormView


from .models import Shipment,Item
from django.views.generic.edit import CreateView
from .forms import ShipmentForm,ItemForm

# def shipmentDetails(request):
#     return render(request,'shipments/sampleShipments.html', {})

class ShipmentDetailView(LoginRequiredMixin, DetailView):
    model = Shipment
    # These next two lines tell the view to index lookups by username
    # As the shipments are based on the user i.e the seller.
    slug_field = 'id'
    slug_url_kwarg = 'id'

# Template View
class ShipmentOrderView(CreateView):
     model = Shipment
     template_name = 'shipments/sampleShipments.html' 
     form_class = ShipmentForm
     #fields  = ['name']
     # Specify the template page where you want to got once it succeeds
     success_url = reverse_lazy('shipments/sampleShipments') 
     def get_context_data(self,**kwargs):
        context = super(ShipmentOrderView,self).get_context_data(**kwargs)
        context['item_form'] = ItemForm()
        return context 
    #Check if the forms is valid,get the data from forms and add it to the DB

     

    