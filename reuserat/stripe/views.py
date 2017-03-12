
from django.shortcuts import render,render_to_response,redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from .models import StripeAccount
import json
import copy
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
import stripe
from config.settings.common import STRIPE_TEST_SECRET_KEY

def retrieve_acct_details(account_id,fieldName):
    acct_details = stripe.Account.retrieve(account_id)
    return HttpResponse(acct_details)

# Address, AccountID
def update_payment_info(secret_key, account_number, account_id):
    stripe.api_key = secret_key  # This is the secret key of the user whose details that should be updated.
    account = stripe.Account.retrieve(account_id)
    print(account.external_accounts)

