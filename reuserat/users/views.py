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
from .forms import UserAddressForm, UserForm
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
        print(self.request.user.payment_type)

        if not (self.request.user.payment_type and self.request.user.address):
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


class UserCompleteSignupView(UserUpdateMixin):
    template_name = 'users/user_complete_signup_form.html'

    def get_success_url(self):
        acct_instance = create_account()  # Call to Stripe View to create a stripe account
        self.request.user.stripe_account = acct_instance
        print("AACCCC IN USEERS", acct_instance.account_id)
        self.request.user.save()
        print("AACCCC IN after USEERS", self.request.user.stripe_account.account_id)
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


class LoginUserCompleteSignupRequiredMixin(LoginRequiredMixin):
    """
    This should be inherited by Classes that should require a complete signup of user (payment info, etc.) before displaying
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch function, and required that a user have filled in payment type and address.
        """
        print(self.request.user.payment_type)

        if not (self.request.user.payment_type and self.request.user.address):
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


class UserCompleteSignupView(UserUpdateMixin):
    template_name = 'users/user_complete_signup_form.html'

    def get_success_url(self):
        # Pass the Ip address of the client.
        # Call to Stripe View to create a stripe account
        print("LALALALALALA")
        account_instance = create_account(self.request.META['REMOTE_ADDR'])
        print("deported")
        if account_instance :
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
    if request.method == "GET":
        country = request.user.address.country
        form = UpdatePaymentForm()  # Create an object for form
        return render(request, "users/user_update_payment.html", {"update_payment_form": form})  # Display Form

    # Get the form data ,so the POST request
    if request.method == "POST":
        print(request.POST,"REQUEST")
        form = UpdatePaymentForm(request.POST)
        request.user.birth_date = datetime.date(int(request.POST['birthdate_year']),
                                                int(request.POST['birthdate_month']),
                                                int(request.POST['birthdate_day']))
        request.user.save()
        if form.is_valid():
            if update_payment_info(str(request.user.stripe_account.account_id), request.POST["stripeToken"],request.user):

                messages.add_message(request, messages.SUCCESS, "Updated")
                return redirect(reverse('users:detail', kwargs={'username': request.user.username}))
            else:
                messages.add_message(request, messages.ERROR, "Server Error!Please try again")

        form = UpdatePaymentForm()

        return render(request, "users/user_update_payment.html", {"update_payment_form": form})


def testCharge(request):
    print("I AM HERE")
    create_charge(request.user)
