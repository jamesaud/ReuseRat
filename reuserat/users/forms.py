from django import forms
from .models import User


class UserCompleteSignupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserCompleteSignupForm, self).__init__(*args, **kwargs)
        # Making all fields required
        for field in self.fields:
            self.fields[field].required = True

        print(self.fields['payment_type'].__dict__)

    class Meta:
        model = User

        fields = ['first_name', 'last_name', 'payment_type', 'phone', 'address',]

        widgets = {
            'payment_type': forms.RadioSelect(),
        }

