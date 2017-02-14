from django import forms


class ShopifyItemRedirectForm(forms.Form):
    item_name = forms.CharField(label="Add New Item", required=True)
    shipment_id = forms.CharField(label="Shipment ID", widget=forms.HiddenInput(), required=True)




