from django import forms
from .models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Address

user = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'payment_type', 'phone',)
        widgets = {
            'payment_type': forms.RadioSelect(),
        }

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('address_line','address_apartment','city','state','zipcode')
