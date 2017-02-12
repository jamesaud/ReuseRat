# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.edit import FormMixin,ProcessFormView
from django.contrib.auth import get_user_model
from .models import User,Address
from .forms import UserAddressForm, UserForm


class LoginUserCompleteSignupRequiredMixin(LoginRequiredMixin):
    """
    This should be inherited by Classes that should require a complete signup of user (payment info, etc.) before displaying
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch function, and required that a user have filled in payment type and address.
        """
        print(self.request.user.address,"pppppp")
        print(self.request.user.payment_type)

        if not (self.request.user.payment_type and self.request.user.address):
           return redirect('users:complete_signup', username=self.request.user.username)

        return super(LoginUserCompleteSignupRequiredMixin, self).dispatch(request, *args, **kwargs)

# Mixin for updating 2 models
class UserUpdateMixin(LoginRequiredMixin,TemplateView,ProcessFormView):

    user_form = UserForm
    address_form = UserAddressForm

    def get_context_data(self, **kwargs):
        context = super(UserUpdateMixin, self).get_context_data(**kwargs)
        context['user_form'] = self.user_form(instance=self.request.user)
        if self.request.user.address:
            context['address_form'] = self.address_form(instance=self.request.user.address)
        else:
            context['address_form'] = self.address_form()
        return context


    def post(self, request, *args, **kwargs):

        user_form = self.user_form(request.POST)
        address_form = self.address_form(request.POST)

        if address_form.is_valid() and user_form.is_valid():
            new_address = Address(**address_form.cleaned_data)
            new_address.save() # Save Address first as there is an FK dependency between User & Address

            # Update the user
            for key, value in user_form.cleaned_data.items():
                setattr(self.request.user, key, value)

            self.request.user.address = new_address
            self.request.user.save()

            return redirect(self.get_success_url())


class UserCompleteSignupView(UserUpdateMixin):

    template_name = 'users/user_complete_signup_form.html'

    def get_success_url(self):
        return reverse('users:detail',
                        kwargs={'username': self.request.user.username})


    def get_context_data(self, **kwargs):
        context = super(UserCompleteSignupView, self).get_context_data(**kwargs)
        context['user_form'] = self.user_form(instance=self.request.user,
                                              initial={'payment_type': 'Paypal'})
        return context


class UserUpdateView(UserUpdateMixin):

    # we already imported User in the view code above, remember?
    template_name = 'users/user_form.html'
    # send the user back to their own page after a successful update

    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})



class UserDetailView(LoginUserCompleteSignupRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginUserCompleteSignupRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})





class UserListView(LoginUserCompleteSignupRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'
