# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, HttpResponse
from django.views.generic.edit import FormMixin, ProcessFormView
from django.contrib.auth import get_user_model
from .models import User, Address
from reuserat.stripe.models import StripeAccount
from .forms import UserAddressForm, UserForm, UserCompleteSignupForm
from reuserat.stripe.forms import UpdatePaymentForm
from reuserat.stripe.helpers import create_account, update_payment_info, create_charge
from django.contrib.auth.decorators import login_required  # new#  import for function based view (FBV)
from django.contrib import messages
from django.conf import settings
import datetime

import stripe

class LoginUserCompleteSignupRequiredMixin(LoginRequiredMixin):
    """
    This should be inherited by Classes that should require a complete signup of user (payment info, etc.) before displaying
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch function, and required that a user have filled in payment type and address.
        """

        if not (self.request.user.completed_signup()):
            return redirect('users:complete_signup', username=self.request.user.username)

        return super(LoginUserCompleteSignupRequiredMixin, self).dispatch(request, *args, **kwargs)


# Mixin for updating 2 models
class UserUpdateMixin(LoginRequiredMixin):
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
        user_form = self.ussr_form(request.POST)
        address_form = self.address_form(request.POST)

        if address_form.is_valid() and user_form.is_valid():
            new_address = Address(**address_form.cleaned_data)
            new_address.save()  # Save Address first as there is an FK dependency between User & Address

            # Update the user
            for key, value in user_form.cleaned_data.items():
                setattr(self.request.user, key, value)

            self.request.user.address = new_address
            self.request.user.save()

            return redirect(self.get_success_url())



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

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)

        # Put shipments with visible items on top.
        context['user_shipments'] = sorted(self.object.shipment_set.all(),
                                           key=lambda s: s.has_visible_items(),
                                           reverse=True)
        return context


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


class LoginUserCompleteSignupRequiredMixin(LoginRequiredMixin):
    """
    This should be inherited by Classes that should require a complete signup of user (payment info, etc.) before displaying
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch function, and required that a user have filled in payment type and address.
        """

        if not request.user.completed_signup():
            return redirect('users:complete_signup', username=self.request.user.username)

        return super(LoginUserCompleteSignupRequiredMixin, self).dispatch(request, *args, **kwargs)


# Mixin for updating 2 models
class UserUpdateMixin(LoginRequiredMixin, TemplateView, ProcessFormView):
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
            new_address.save()  # Save Address first as there is an FK dependency between User & Address

            # Update the user
            for key, value in user_form.cleaned_data.items():
                setattr(self.request.user, key, value)

            self.request.user.address = new_address
            self.request.user.save()

            return redirect(self.get_success_url())

        else:
            context = self.get_context_data(**kwargs)
            context['address_form'] = address_form
            context['user_form'] = user_form
            return render(request, self.template_name, context)


class UserCompleteSignupView(UserUpdateMixin):
    template_name = 'users/user_complete_signup_form.html'
    user_form = UserCompleteSignupForm

    def get_success_url(self):
        # Pass the Ip address of the client.
        # Call to Stripe View to create a stripe account
        account_instance = create_account(self.request.META['REMOTE_ADDR'])
        if account_instance:
            self.request.user.stripe_account = account_instance
            self.request.user.save()

        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super(UserCompleteSignupView, self).get_context_data(**kwargs)
        context['user_form'] = self.user_form(instance=self.request.user,
                                              initial={'payment_type': 'Paypal'})
        return context


class UserUpdateView(UserUpdateMixin):
    # we already imported User in the view code above, remember?

    model = User
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


@login_required
def update_payment_information(request):
    form = UpdatePaymentForm(request.POST or None, initial={"birth_date": request.user.birth_date,
                                                            "account_holder_name": request.user.get_full_name(),
                                                            })

    # Get the form data ,so the POST request
    if request.method == "POST" and form.is_valid():
        request.user.birth_date = datetime.date(int(request.POST['birthdate_year']),
                                                int(request.POST['birthdate_month']),
                                                int(request.POST['birthdate_day']))
        request.user.save()

        if update_payment_info(str(request.user.stripe_account.account_id), request.POST["stripeToken"], request.user):
            messages.add_message(request, messages.SUCCESS, "Updated Successfully")
            return redirect(reverse('users:detail', kwargs={'username': request.user.username}))

        else:
            messages.add_message(request, messages.ERROR, "Server Error! Please try again later.")


    return render(request, "users/user_update_payment.html", {"update_payment_form": form})
