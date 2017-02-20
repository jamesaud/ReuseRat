from django import forms
from .models import User
from django.utils.translation import ugettext_lazy as _


class UserCompleteSignupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserCompleteSignupForm, self).__init__(*args, **kwargs)

        # Make all fields required
        #for field in self.fields:
        #    self.fields[field].required = True

    class Meta:
        model = User

        fields = ['first_name', 'last_name', 'payment_type', 'phone', 'address', 'address_apartment']

        labels = {
            "address": _("Your Address"),
        }

        widgets = {
            'payment_type': forms.RadioSelect(),
        }

