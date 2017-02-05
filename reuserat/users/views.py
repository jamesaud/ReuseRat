# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.edit import FormMixin

from .models import User
from .forms import UserCompleteSignupForm


class LoginUserCompleteSignupRequiredMixin(LoginRequiredMixin):
    """
    This should be inherited by Classes that should require a complete signup of user (payment info, etc.) before displaying
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch function, and required that a user have filled in payment type and address.
        """
        if not (self.request.user.payment_type and self.request.user.address):
           return redirect('users:complete_signup', username=self.request.user.username)

        return super(LoginUserCompleteSignupRequiredMixin, self).dispatch(request, *args, **kwargs)


class UserCompleteSignupView(LoginRequiredMixin, UpdateView):

    form_class = UserCompleteSignupForm
    initial = {'payment_type': 'Paypal'}
    model = User
    template_name_suffix = '_complete_signup_form'

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super(UserCompleteSignupView, self).get_context_data(**kwargs)
        return context

    #def get_initial(self):
    #    return {'payment_type': 'Paypal'}


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


class UserUpdateView(LoginUserCompleteSignupRequiredMixin, UpdateView):

    fields = ['first_name', 'last_name', 'payment_type', 'phone', 'address']

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        return context



class UserListView(LoginUserCompleteSignupRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'
