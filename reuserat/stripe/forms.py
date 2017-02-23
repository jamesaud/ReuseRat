from django import forms
from crispy_forms.helper import FormHelper
from django.conf import settings
from django.forms import extras

# https://stripe.com/docs/ach#manually-collecting-and-verifying-bank-accounts
# We are not using the Plaid integration because :
# If your customer’s bank is not supported or you do not wish to integrate with Plaid,
# collect and verify the customer’s bank using Stripe alone.
class UpdatePaymentForm(forms.Form):
    PUBLISHABLE_KEY= settings.STRIPE_TEST_PUBLISHABLE_KEY
    """
    Form for updating payment information like account number and routing number for making transaction .
    """
    account_number = forms.IntegerField(required=True,label='Account Number',
                                        widget=forms.TextInput(attrs={'data-stripe' : 'account_number'}))

    account_holder_name = forms.CharField(required=True, label='Account Holder Name',
                                          widget=forms.TextInput(attrs={'data-stripe': 'account_holder_name'}))

    routing_number = forms.IntegerField(required=True,label='Routing Number',
                                        widget=forms.TextInput(attrs={'data-stripe' : 'routing_number'}))

    birthdate = forms.DateField(required=True,widget=extras.SelectDateWidget(years=[y for y in range(1930,2017)]))


    # Hidden Fields,supplied by default
    country = forms.CharField(initial="US",label='Country',widget=forms.HiddenInput(attrs={'data-stripe' : 'country'}))

    currency = forms.CharField(initial="USD",label='Currency',widget=forms.HiddenInput(attrs={'data-stripe' : 'currency'}))

    account_holder_type = forms.CharField(initial="individual",required=True,label='Account Holder Type',
                                          widget=forms.HiddenInput(attrs={'data-stripe' : 'account_holder_type'}))

    def __init__(self, *args, **kwargs):
        super(UpdatePaymentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

    class Media:
        js = ('https://js.stripe.com/v2/',)

