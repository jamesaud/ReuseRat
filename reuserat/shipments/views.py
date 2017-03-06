# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy,reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, FormView
from django.views.generic.edit import CreateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ShipmentForm
from reuserat.users.models import User
from .models import Shipment
from django.apps import apps


from django.contrib.auth.decorators import login_required # new import for function based view (FBV)

from django_pdfkit import PDFView

from django.contrib import messages


class ShipmentDetailView(LoginRequiredMixin,DetailView):
    model = Shipment
    # These next two lines tell the view to index lookups by username
    # As the shipments are based on the user i.e the seller.
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, **kwargs):
        context = super(ShipmentDetailView, self).get_context_data(**kwargs)
        visible_items = [item for item in self.object.item_set.all() if item.is_visible]
        context['visible_items'] = visible_items or None
        return context


# Create View
class ShipmentOrderView(LoginRequiredMixin, CreateView):
     model = Shipment
     template_name = 'shipments/shipment_create.html'
     form_class = ShipmentForm

     # Specify the template page where you want to go once it succeeds
     def get_success_url(self):
         return reverse('shipments:shipmentDetail',kwargs={'pk': self.object.id})

     def get_context_data(self, **kwargs):
        context = super(ShipmentOrderView,self).get_context_data(**kwargs)
        context['user'] = self.object
        context['shipment'] = apps.get_model('shipments', 'Shipment')
        return context

     def form_valid(self, form):
        #Automatically saved so the responsiblity of adding user id
        form.instance.user_id = self.request.user.id
        return super(ShipmentOrderView, self).form_valid(form)


class ShipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Shipment
    template_name = 'shipments/shipment_update.html'
    form_class = ShipmentForm

    def get_success_url(self):
         return reverse('shipments:shipmentDetail', kwargs={'pk': self.object.id})


class ShipmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Shipment

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        if not self.object.item_set.exists():
            self.object.delete()
            messages.success(request, "Successfully deleted shipment.")
        else:
            messages.error(request, "Can't delete shipment with items!")

        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
         return reverse('users:detail', kwargs={'username': self.request.user.username})




class ShipmentPdfView(LoginRequiredMixin,PDFView):
    template_name = 'shipments/shipment_label.html'

    def get_context_data(self, **kwargs):
        context = super(ShipmentPdfView, self).get_context_data(**kwargs)
        context['user'] = self.request.user #apps.get_model('User')
        context['shipment'] =get_object_or_404(Shipment,pk=self.kwargs.get('shipment_id'))
        return context


#Function Based Views
@login_required
def get_shipment_label(request, shipment_id):
    context = {}
    context['user'] = User.objects.get(pk=request.user.id) #apps.get_model('User')
    context['shipment'] = Shipment.objects.get(pk=shipment_id) #apps.get_model('Shipment')
    return render(request, 'shipments/shipment_label.html', context)

