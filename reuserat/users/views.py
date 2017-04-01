# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import defaultdict

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import ProcessFormView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from stripe.error import StripeError

from .models import User, Address, PaymentChoices
from .forms import UserAddressForm, UserForm, UserCompleteSignupForm

from reuserat.stripe.models import PaypalAccount, Transaction, TransactionTypeChoices
from reuserat.stripe.forms import UpdatePaymentForm, PaypalUpdateForm, UserPaymentForm
from reuserat.stripe import helpers as stripe_helpers
from reuserat.stripe.tests import helpers as test_stripe_helpers
from reuserat.stripe import paypal_helpers, check_helpers

import time
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class LoginUserCompleteSignupRequiredMixin(LoginRequiredMixin):
    """
    This should be inherited by Classes that should require a complete signup of user (payment info, etc.) before displaying
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch function, and required that a user have filled in payment type and address.
        """

        if not (self.request.user.has_completed_signup()):
            return redirect('users:complete_signup')

        return super().dispatch(request, *args, **kwargs)


class UserDetailView(LoginUserCompleteSignupRequiredMixin, TemplateView):
    model = User
    template_name = 'users/user_detail.html'
    # These next two lines tell the view to index lookups by username
    items_to_show = 3  # Items to show in html
    description_characters = 220  # Characters of description to show in html
    min_cash_out_amount = 5.00 # In dollars

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Put shipments with visible items on top.
        context['user_shipments'] = sorted(self.request.user.shipment_set.all(),
                                           key=lambda s: s.has_visible_items(),
                                           reverse=True)
        context['object'] = self.request.user
        context['items_to_show'] = self.items_to_show
        context['balance'] = self.request.user.get_current_balance()
        context['min_cash_out_amount'] = self.min_cash_out_amount
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

        print(user_form.errors)
        print(address_form.errors)

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
        account_instance = stripe_helpers.create_account(self.request.META['REMOTE_ADDR'])
        if account_instance:
            self.request.user.stripe_account = account_instance
            self.request.user.save()

        # Create default paypal account for the user.
        paypal = PaypalAccount(email=self.request.user.get_primary_email())
        paypal.save()
        self.request.user.paypal_account = paypal
        self.request.user.save()

        return reverse('users:detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = self.user_form(instance=self.request.user,
                                              initial={'payment_type': 'Paypal'})
        return context


class UserUpdateView(LoginUserCompleteSignupRequiredMixin, UserUpdateMixin):
    # we already imported User in the view code above, remember?

    model = User
    template_name = 'users/user_form.html'

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail')


class UserRedirectView(LoginUserCompleteSignupRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail')


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class TransactionListView(LoginRequiredMixin, TemplateView):
    model = Transaction
    template_name = 'users/user_transactions.html'
    slug_field = 'transactions'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) or {}
        transaction_list = self.request.user.transaction_set.all()
        paginator = Paginator(transaction_list, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            transactions = paginator.page(page)
        except PageNotAnInteger:
            transactions = paginator.page(1)
        except EmptyPage:
            transactions = paginator.page(paginator.num_pages)

        # Associate a color with Transaction type
        css_lookup = defaultdict(lambda: 'default')  # Set the color to grey if we didn't register it in the dictionary
        css_lookup.update({TransactionTypeChoices.IN: 'success',
                           TransactionTypeChoices.OUT: 'info',
                           TransactionTypeChoices.FEE: 'danger',
                           TransactionTypeChoices.CREDIT: 'warning', })
        context.update({'transaction_set': transactions, 'transaction_type_css_lookup': css_lookup})
        return context


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
        stripe_form = stripe_form or self.StripeForm(initial={"birth_date": self.request.user.birth_date,
                                                              "account_holder_name": stripe.account_holder_name or self.request.user.get_full_name(),
                                                              "account_number": account_number,
                                                              "routing_number": routing_number, })

        # Set the Paypal Form defaults
        paypal_form = paypal_form or self.PaypalForm(
            choices=self.PaypalFormChoices,
            initial={'email': self.request.user.paypal_account.email.email})

        user_payment_form = user_payment_form or self.UserForm(initial={'payment_type': self.request.user.payment_type})

        context.update({"update_payment_form": stripe_form,
                        "paypal_form": paypal_form,
                        "user_payment_form": user_payment_form,
                        "payment_choices": PaymentChoices})
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

        user.birth_date = form.cleaned_data['birth_date']  # datetime.date instance.
        user.save()  # So we can use the birthdate

        # Update the user's bank Stripe Banking info.
        try:
            account = stripe_helpers.update_payment_info(str(user.stripe_account.account_id),
                                                         request.POST["stripeToken"], user)
        except StripeError as e:
            logger.error("Failed to update stripe account: " + str(e))
            messages.add_message(request, messages.ERROR, "Server Error! That's on us. Please try again later.")
            return False
        else:
            user.stripe_account.account_holder_name = form.cleaned_data['account_holder_name']
            user.stripe_account.account_number_last_four = str(form.cleaned_data['account_number'])[-4:]
            user.stripe_account.routing_number_last_four = str(form.cleaned_data['routing_number'])[-4:]
            user.stripe_account.account_number_length = len(str(form.cleaned_data['account_number']))
            user.stripe_account.save()
            user.save()
            messages.add_message(request, messages.SUCCESS, "Updated Bank Successfully")
            return form

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
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        """All the 'use_<whatever>' functions should return a Transaction object, or raise an error."""
        payment_type = self.request.user.payment_type

        try:
            if payment_type == PaymentChoices.PAYPAL:
                transaction = self.use_paypal()

            elif payment_type == PaymentChoices.DIRECT_DEPOSIT:
                transaction = self.use_direct_deposit()

            elif payment_type == PaymentChoices.CHECK:
                transaction = self.use_check()

        except (paypal_helpers.PaypalException, StripeError):
            # Exception code goes here. Exception is being logged in the relevant function.
            # Return the same page with error messages (created in the functions)
            return redirect(self.get_success_url())

        else:
            return redirect(self.get_success_url())

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def use_direct_deposit(self):
        # Amount to be transferred is the balance money in the stripe account
        balance_in_cents = self.request.user.stripe_account.retrieve_balance()
        try:
            transfer_id = stripe_helpers.create_transfer_bank(api_key=self.request.user.stripe_account.secret_key,
                                                              # User's Bank account,
                                                              balance_in_cents=balance_in_cents,  # Amount to transfer
                                                              user_name=self.request.user.get_full_name())
        except StripeError as e:
            logger.error("Stripe Cash Out Exception: " + str(e))
            messages.add_message(self.request, messages.ERROR, 'Failed to cash out using Direct Deposit: ' + str(e))
            raise
        else:
            transaction = Transaction(user=self.request.user,
                                      payment_type=self.request.user.payment_type,
                                      message="Cash Out with Direct Deposit",
                                      type=TransactionTypeChoices.OUT,
                                      amount=stripe_helpers.cents_to_dollars(balance_in_cents))
            transaction.save()
            messages.add_message(self.request, messages.SUCCESS,
                                 'Cashed out using Direct Deposit successfully. Check the status at My Account > Transactions')
            return transaction

    def use_paypal(self):
        balance_in_cents = int(self.request.user.stripe_account.retrieve_balance())
        balance_in_dollars = stripe_helpers.cents_to_dollars(balance_in_cents)

        try:
            # Try to transfer the user's current balance to OUR stripe account.
            transfer_id = stripe_helpers.create_transfer_to_platform(
                account_id=self.request.user.stripe_account.account_id,
                balance_in_cents=balance_in_cents,
                description="Cashing out using Paypal")

        except StripeError as e:
            logger.error("Paypal Cash Out Exception (stripe error): " + str(e))
            messages.add_message(self.request, messages.ERROR,
                                 "Cashout with Paypal failed. That's our fault. Please try again later.")
            raise

        try:
            # Try to send the user money via Paypal Mass Payments API
            paypal_response = paypal_helpers.make_payment_paypal(
                batch_id='u-{0}-t-{1}'.format(self.request.user.id, time.time()),  # Transaction ID is unique
                receiver_email=self.request.user.paypal_account.email.email,  # Send to the user's selected paypal email
                amount_in_dollars=balance_in_dollars,
                note="Your Cashout, With Love from ReuseRat")

        except paypal_helpers.PaypalException as e:
            # Reverse the transfer because we couldn't cash a user out to Paypal.
            stripe_helpers.reverse_transfer(transfer_id, self.request.user.stripe_account.secret_key)
            logger.error("Paypal Cash Out Exception: " + str(e))

            # Handle specific Paypal errors to add specific messages
            if isinstance(e, paypal_helpers.PaypalReceiverUnregistered):
                messages.add_message(self.request, messages.ERROR,
                                     "Paypal Account using email {} doesn't exist or is unregistered! Please add an existing Paypal email or contact support.".format(
                                         self.request.user.paypal_account.email.email))
            else:
                messages.add_message(self.request, messages.ERROR,
                                     "Cashout with Paypal failed, that's (probably) our fault! Please try again later.")
            raise
        else:
            # Create the transaction
            transaction = Transaction(user=self.request.user,
                                      payment_type=self.request.user.payment_type,
                                      message="Cash Out with Paypal using email " + self.request.user.paypal_account.email.email,
                                      type=TransactionTypeChoices.OUT,
                                      amount=balance_in_dollars)  # Need to set the balance still

            transaction.save()  # Will delete if the api calls don't go through. Need the transaction ID to set as the paypal batch id.

            messages.add_message(self.request, messages.SUCCESS,
                                 'Cashed out using Paypal successfully. Please accept the email sent to {}. To resend the email, please go to My Account > Transactions.'.format(
                                     self.request.user.paypal_account.email.email))
            return transaction

    def use_check(self):
        # To get the amount of money to be transferred through check
        balance_in_cents = int(self.request.user.stripe_account.retrieve_balance())
        balance_in_dollars = stripe_helpers.cents_to_dollars(balance_in_cents)
        customer_name = self.request.user.get_full_name()

        try:
            # Try to transfer the user's current balance to OUR stripe account.
            transfer_id = stripe_helpers.create_transfer_to_platform(
                account_id=self.request.user.stripe_account.account_id,
                balance_in_cents=balance_in_cents,
                description="Cashing out using Check")

        except StripeError as e:
            logger.error("Paypal Cash Out Exception (stripe error): " + str(e))
            messages.add_message(self.request, messages.ERROR,
                                 "Cashout with Check failed. That's our fault. Please try again later.")
            raise


        # Next step is to use the LOB API to send the check
        try:
            address_line1 = self.request.user.address.address_line
            address_line2 = self.request.user.address.address_apartment
            city = self.request.user.address.city
            state = self.request.user.address.state
            zipcode = self.request.user.address.zipcode
            country = self.request.user.address.country
            check_response = check_helpers.create_check(customer_name,address_line1,address_line2,city,state,zipcode,country,balance_in_dollars)

            print(check_response)
        except Exception as e:
            logger.error("Check Error: " + str(e))
            raise
        else:
            # Create the transaction
            transaction = Transaction(user=self.request.user,
                                      payment_type=self.request.user.payment_type,
                                      message="Cash Out with Check ",
                                      type=TransactionTypeChoices.OUT,
                                      amount=balance_in_dollars,
                                      check_id=check_response.id)  # Need to set the balance still

            transaction.save()  # Will delete if the api calls don't go through. Need the transaction ID to set as the paypal batch id.

            messages.add_message(self.request, messages.SUCCESS,
                                 'Cashed out using Check successfully. The expected delivery date is {}.'.format(check_response.expected_delivery_date))
            return check_response
