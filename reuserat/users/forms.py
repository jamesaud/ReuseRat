from django import forms
from .models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Address

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field
from django.forms import extras


class UserCompleteSignupForm(forms.ModelForm):
    birth_date = forms.DateField(required=True,
                                label='Birth Date',
                                widget=extras.SelectDateWidget(years=[y for y in range(1930,2017)]))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'payment_type', 'phone', 'birth_date')
        widgets = {
            'payment_type': forms.RadioSelect(),
        }
        labels = {
            'phone': 'Phone xxx-xxx-xxxx',
        }



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')
        labels = {
            'phone': 'Phone xxx-xxx-xxxx',
        }


    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                    Div('first_name',css_class="col-md-6"),
                    Div('last_name',css_class="col-md-6"),
                    Div('phone', css_class="col-md-6"),
                )

        self.helper.form_tag = False




class UserAddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ('address_line', 'address_apartment', 'city', 'state', 'zipcode')


    def __init__(self, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                    Div('address_line',css_class="col-md-6"),
                    Div('address_apartment',css_class="col-md-6"),
                    Div('city', css_class="col-md-6"),
                    Div('state', css_class="col-md-6"),
                    Div('zipcode', css_class="col-md-6"),
                )

        self.helper.form_tag = False

