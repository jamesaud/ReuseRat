from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field


class ShopifyItemRedirectForm(forms.Form):
    item_name = forms.CharField(label="",
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Item Name'}))

    shipment_id = forms.CharField(label="Shipment ID",
                                  widget=forms.HiddenInput(),
                                  required=True)



