# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, HttpResponse
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.decorators import login_required  # new#  import for function based view (FBV)
from django.contrib import messages

from allauth.account.models import EmailAddress

from .models import User, Address, PaymentChoices
from .forms import UserAddressForm, UserForm, UserCompleteSignupForm

from reuserat.stripe.models import PaypalAccount
from reuserat.stripe.forms import UpdatePaymentForm, PaypalUpdateForm, UserPaymentForm
from reuserat.stripe.helpers import create_account, update_payment_info

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

        if not (self.request.user.has_completed_signup()):
            return redirect('users:complete_signup', username=self.request.user.username)

        return super(LoginUserCompleteSignupRequiredMixin, self).dispatch(request, *args, **kwargs)



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

        #Create default paypal account for the user.
        paypal = PaypalAccount(email=self.request.user.get_primary_email())
        paypal.save()
        self.request.user.paypal_account = paypal
        self.request.user.save()

        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super(UserCompleteSignupView, self).get_context_data(**kwargs)
        context['user_form'] = self.user_form(instance=self.request.user,
                                              initial={'payment_type': 'Paypal'})
        return context


class UserUpdateView(LoginUserCompleteSignupRequiredMixin, UserUpdateMixin):
    # we already imported User in the view code above, remember?

    model = User
    template_name = 'users/user_form.html'

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})




class UserRedirectView(LoginUserCompleteSignupRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'



@login_required
def update_payment_information(request):


    # Set the default bank values to be the last four digits preappended with '*'s
    account_number = routing_number = None
    if request.user.stripe_account.has_bank():
        stripe = request.user.stripe_account
        account_number = (stripe.account_number_length - 4) * '*' + str(stripe.account_number_last_four)
        routing_number = '*' * 5 + stripe.routing_number_last_four

    stripe_form = UpdatePaymentForm(request.POST or None, initial={"birth_date": request.user.birth_date,
                                                                   "account_holder_name": request.user.get_full_name(),
                                                                   "account_number": account_number,
                                                                   "routing_number": routing_number,
                                                            })

    # Choices must be a list of tuples. Set's the available email choices to the user's verified emails.
    paypal_form = PaypalUpdateForm(choices=((email.email, email.email) for email in request.user.get_verified_emails()),
                                   data=request.POST or None,
                                   initial={'email': request.user.paypal_account.email.email})

    user_payment_form = UserPaymentForm(request.POST or None,)

    # For Post Requests
    if request.method == "POST" and user_payment_form.is_valid():
        choice = user_payment_form.cleaned_data['payment_type']

        # Update the payment Choice.
        user = request.user
        user.payment_type = choice
        user.save()

        # We don't need to do anything if it's a check payment.
        if choice == PaymentChoices.CHECK:
            pass

        # Handle as Stripe Payment
        elif choice == PaymentChoices.DIRECT_DEPOSIT and stripe_form.is_valid():

            user.birth_date = datetime.date(int(request.POST['birthdate_year']),
                                                    int(request.POST['birthdate_month']),
                                                    int(request.POST['birthdate_day']))
            user.save()

            # Update the user's bank Stripe Banking info.
            account = update_payment_info(str(user.stripe_account.account_id), request.POST["stripeToken"], user)
            if account:
                messages.add_message(request, messages.SUCCESS, "Updated Successfully")
                return redirect(reverse('users:detail', kwargs={'username': user.username}))
            else:
                messages.add_message(request, messages.ERROR, "Server Error! Please try again later.")


        # Handle as Paypal
        elif choice == PaymentChoices.PAYPAL and paypal_form.is_valid():
            # Get the email object associated with the string passed in POST data.
            email_obj = user.emailaddress_set.filter(email=paypal_form.cleaned_data['email']).first()

            # If the email is the same, do nothing, else update.
            if email_obj is not user.paypal_account.email:
                # Use get_or_create, because the PayPal account for the email might exist if the user switched emails before
                paypal_obj, created = PaypalAccount.objects.get_or_create(email=email_obj)
                user.paypal_account = paypal_obj
                user.save()


    # For GET or any other requests
    return render(request, "users/user_update_payment.html", {"update_payment_form": stripe_form,
                                                              "paypal_form": paypal_form,
                                                              "user_payment_form": UserPaymentForm,
                                                              "payment_choices": PaymentChoices
                                                              })
