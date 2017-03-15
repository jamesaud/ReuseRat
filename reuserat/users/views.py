# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required  # new#  import for function based view (FBV)
from django.contrib import messages
from django.shortcuts import redirect, render, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import  ProcessFormView

from .models import User, Address, PaymentChoices
from .forms import UserAddressForm, UserForm, UserCompleteSignupForm

from reuserat.stripe.models import PaypalAccount
from reuserat.stripe.forms import UpdatePaymentForm, PaypalUpdateForm, UserPaymentForm
from reuserat.stripe.helpers import create_account, update_payment_info, create_transfer
from reuserat.stripe.paypal_helpers import make_payment_paypal

import pprint

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

        # Create default paypal account for the user.
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


class UpdatePaymentInformation(LoginUserCompleteSignupRequiredMixin, TemplateView, ProcessFormView):
    """
    This view processes multiple payment forms.
    The logic for each goes in it's own method, 'process_<name>(request, form):'
    Each 'process_<name>' method should return the form if successful, if failure return False.
    """

    template_name = "users/user_update_payment.html"

    StripeForm = UpdatePaymentForm
    PaypalForm = PaypalUpdateForm
    PaypalFormChoices = None  # Set in dispatch
    UserForm = UserPaymentForm

    def dispatch(self, request, *args, **kwargs):
        """
        Set the PaypalFormChoices to be the user's verified emails. Choices must be a list of tuples.
        :return:
        """
        self.PaypalFormChoices = ((email.email, email.email) for email in self.request.user.get_verified_emails())
        return super().dispatch(request, *args, **kwargs)

        if address_form.is_valid() and user_form.is_valid():
            new_address = Address(**address_form.cleaned_data)
            new_address.save()  # Save Address first as there is an FK dependency between User & Address

    def get_success_url(self):
        return reverse('users:update_payment_information')

    def get_context_data(self, stripe_form=None, user_payment_form=None, paypal_form=None, **kwargs):
        """
        Set's the forms and returns the context.
        Pass forms to optionally use, useful for setting forms on invalid POST submissions.
        """
        context = super().get_context_data(**kwargs) or {}
        account_number = routing_number = None
        stripe = self.request.user.stripe_account

        # Set the routing and account placeholder numbers if a bank is already registered with a user.
        if stripe.has_bank():
            account_number = (stripe.account_number_length - 4) * '*' + str(stripe.account_number_last_four)
            routing_number = '*' * 5 + stripe.routing_number_last_four

        # Set the Stripe form initial values. Set account_holder_name to the user's name if it's null.
        stripe_form = stripe_form or self.StripeForm(
            initial={"birth_date": self.request.user.birth_date,
                     "account_holder_name": stripe.account_holder_name or self.request.user.get_full_name(),
                     "account_number": account_number,
                     "routing_number": routing_number,
                     })

        # Set the Paypal Form defaults
        paypal_form = paypal_form or self.PaypalForm(
            choices=self.PaypalFormChoices,
            initial={'email': self.request.user.paypal_account.email.email})

        user_payment_form = user_payment_form or self.UserForm(initial={'payment_type': self.request.user.payment_type})

        context.update({"update_payment_form": stripe_form,
                        "paypal_form": paypal_form,
                        "user_payment_form": user_payment_form,
                        "payment_choices": PaymentChoices
                        })
        return context

    def post(self, *args, **kwargs):
        """
        Triggers the correct form to process depending on which choice the user made.
        """
        user = self.request.user
        stripe_form = self.StripeForm(self.request.POST)
        user_payment_form = self.UserForm(self.request.POST)
        paypal_form = self.PaypalForm(choices=self.PaypalFormChoices,
                                      data=self.request.POST)

        if user_payment_form.is_valid():
            choice = user_payment_form.cleaned_data['payment_type']
            success = False

            # Update the user's payment type.
            user.payment_type = choice
            user.save()

            # Process the correct form depending on the choice and if the form is valid.
            if choice == PaymentChoices.DIRECT_DEPOSIT and stripe_form.is_valid():
                success = self.process_stripe(stripe_form)

            elif choice == PaymentChoices.PAYPAL and paypal_form.is_valid():
                success = self.process_paypal(paypal_form)

            elif choice == PaymentChoices.CHECK:
                success = self.process_check(form=None)

            if success:
                return HttpResponseRedirect(self.get_success_url())

        # If there is a failure, return the same page with form errors.
        return self.render_to_response(self.get_context_data(stripe_form=stripe_form,
                                                             paypal_form=paypal_form,
                                                             user_payment_form=user_payment_form,
                                                             status_code=400))  # Error, so 400 status code.

    def process_check(self, form):
        """ Don't need to do anything to process Check. """
        messages.add_message(self.request, messages.SUCCESS, "Updated Check Successfully")
        return True

    def process_stripe(self, form):

        """
        Hits the Stripe API to update the user's account.
        Updates the User's StripeAccount with the new details.
        """
        user, request = self.request.user, self.request

        # Update the user's bank Stripe Banking info.
        account = update_payment_info(str(user.stripe_account.account_id), request.POST["stripeToken"], user)
        if account:  # Update User's Stripe account in our database
            user.birth_date = form.cleaned_data['birth_date']  # datetime.date instance.
            user.stripe_account.account_holder_name = form.cleaned_data['account_holder_name']
            user.stripe_account.account_number_last_four = str(form.cleaned_data['account_number'])[-4:]
            user.stripe_account.routing_number_last_four = str(form.cleaned_data['routing_number'])[-4:]
            user.stripe_account.account_number_length = len(str(form.cleaned_data['account_number']))
            user.stripe_account.save()
            user.save()
            messages.add_message(request, messages.SUCCESS, "Updated Bank Successfully")
            return form
        else:
            messages.add_message(request, messages.ERROR, "Server Error! Please try again later.")
            return False

    def process_paypal(self, form):
        user, request = self.request.user, self.request

        # Get the object associated with the email passed in POST data.
        email_obj = user.emailaddress_set.filter(email=form.cleaned_data['email']).first()

        # If the email is not their Paypal email, then update.
        if email_obj is not user.paypal_account.email:
            # Use get_or_create, because the PayPal account may exist if the user switched emails before.
            paypal_obj, created = PaypalAccount.objects.get_or_create(email=email_obj)
            user.paypal_account = paypal_obj
            user.save()

        messages.add_message(self.request, messages.SUCCESS, "Updated Paypal Successfully")
        return form


class CashOutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        payment_type = self.request.user.payment_type

        if payment_type == PaymentChoices.PAYPAL:
            response = self.use_paypal()
            return HttpResponse(response)


        elif payment_type == PaymentChoices.DIRECT_DEPOSIT:
            self.use_direct_deposit()

        elif payment_type == PaymentChoices.CHECK:
            self.use_check()

    def use_paypal(self):
        return str(make_payment_paypal(batch_id='batch_{}'.format(),
                                       receiver_email="trashandtreasure67-buyer-1@gmail.com",
                                       amount=1000,
                                       note="Thanks for all the fish"))

    def use_direct_deposit(self):
        pass

    def use_check(self):
        pass



@login_required
def cash_out(request):
    if request.method == 'GET':
        # Get the Stripe account id of the User
        account_id = request.user.stripe_account.account_id

        # Amount to be transferred is the balance money in the stripe account
        balance_in_cents = int(request.user.get_current_balance() * 100)

        # Get the user's full name for the description in the transfer
        user_name = request.user.get_full_name()

        transfer_id = create_transfer(account_id, balance_in_cents, user_name)

        return redirect(reverse('users:detail', kwargs={'username': request.user.username}))
