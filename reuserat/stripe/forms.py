from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field, MultiWidgetField
from django.forms import extras
from django.conf import settings
from reuserat.users.models import PaymentChoices
from .models import PaypalAccount

# https://stripe.com/docs/ach#manually-collecting-and-verifying-bank-accounts
# We are not using the Plaid integration because :
# If your customer’s bank is not supported or you do not wish to integrate with Plaid,
# collect and verify the customer’s bank using Stripe alone.
class UpdatePaymentForm(forms.Form):
    """
    Form for updating payment information like account number and routing number for making transaction .
    """

    PUBLISHABLE_KEY = settings.STRIPE_TEST_PUBLISHABLE_KEY  # Required by the stripe javascript call.

    account_number = forms.CharField(required=True,label='Account Number',
                                        widget=forms.TextInput(attrs={'data-stripe' : 'account_number'}))

    account_holder_name = forms.CharField(required=True, label='Account Holder Name',
                                          widget=forms.TextInput(attrs={'data-stripe': 'account_holder_name'}))

    routing_number = forms.CharField(required=True,label='Routing Number',
                                        widget=forms.TextInput(attrs={'data-stripe' : 'routing_number'}))

    birth_date = forms.DateField(required=True,
                                label='Birth Date (for verifying account)',
                                widget=extras.SelectDateWidget(years=[y for y in range(1930,2017)]))


    # Hidden Fields,supplied by default
    country = forms.CharField(initial="US",label='Country',widget=forms.HiddenInput(attrs={'data-stripe' : 'country'}))

    currency = forms.CharField(initial="USD",label='Currency',widget=forms.HiddenInput(attrs={'data-stripe' : 'currency'}))

    account_holder_type = forms.CharField(initial="individual",required=True,label='Account Holder Type',
                                          widget=forms.HiddenInput(attrs={'data-stripe' : 'account_holder_type'}))

    def __init__(self, *args, **kwargs):
        super(UpdatePaymentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
               Div('account_number', css_class="col-md-6"),
            Div('routing_number', css_class="col-md-6"),
            Div('account_holder_name', css_class="col-md-6"),
            Div(MultiWidgetField('birth_date',
                                 attrs=({'style': 'width: 32%; display: inline-block;'})),
                                 css_class="col-md-6"),
         
            'country',
            'currency',
            'account_holder_type'
        )

        self.helper.form_tag = False
        self.helper.include_media = False

    class Media:
        # Extra js classes are needed to make the circle radio buttons work.
        js = ('https://js.stripe.com/v2/',
              'standalone/material-bootstrap-wizard-v1.0.1/assets/js/jquery.bootstrap.js',
              'standalone/material-bootstrap-wizard-v1.0.1/assets/js/bootstrap.min.js',
              'standalone/material-bootstrap-wizard-v1.0.1/assets/js/jquery.validate.min.js',
              'standalone/material-bootstrap-wizard-v1.0.1/assets/js/material-bootstrap-wizard.js',

              )



class PaypalUpdateForm(forms.Form):
    email = forms.ChoiceField(widget=forms.RadioSelect,
                              label='Choose an email to use with Paypal',
                              choices=(['email', 'www.email@example.com'],))

    def __init__(self, choices, *args, **kwargs):
        """
        :param choices: A list of valid emails for the paypal update form, found from the user's verified emails.
        """
        super().__init__(*args, **kwargs)
        self.fields['email'].choices = choices


class UserPaymentForm(forms.Form):
    payment_type = forms.ChoiceField(widget=forms.RadioSelect, choices=PaymentChoices.CHOICES)

