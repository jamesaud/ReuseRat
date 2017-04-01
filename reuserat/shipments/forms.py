from django.forms import ModelForm, Textarea, ClearableFileInput
from .models import Shipment
from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Layout, Div, Field
from crispy_forms.helper import FormHelper


class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        fields =['name','description']
        labels = {
            'name': _('Shipment Name'),
        }

        widgets = {
            'description': Textarea(attrs={'cols': 0, 'rows': 0}),
        }


class ShipmentDetailTrackingForm(ModelForm):
    class Meta:
        model = Shipment
        fields = ['tracking_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tracking_number'].required = True 


class ShipmentDetailReceiptForm(ModelForm):
    """Update Tracking and Receipt in Shipment Details Page"""
    class Meta:
        model = Shipment
        fields = ['receipt']

        widgets = {
            'receipt': ClearableFileInput(attrs={'class': 'file', 'data-show-preview':'false'})
        }
        labels = {
            'receipt': _('Add Receipt Here'),
        }

    def __init__(self, *args, **kwargs):
        super(ShipmentDetailReceiptForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                    Field('receipt', css_class='file', ),
                )

        self.helper.form_tag = False
        self.helper.form_show_labels = False

        # Important to have it is as required for processsing the 2 forms correctly
        self.fields['receipt'].required = True 
