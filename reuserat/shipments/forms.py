from django.forms import ModelForm
from .models import Shipment
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _


class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        fields =['name','description']
        labels = {
            'name': _('Shipment Name'),
        }

