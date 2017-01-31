from django.forms import ModelForm
from .models import Shipment,Item
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

class ItemForm(ModelForm):
     class Meta:
            model = Item
            fields = ['name','description']
            labels = {
            'name': _('Item Name'),
            'description': _('Item Description'),
            }


class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        fields =['name']
        labels = {
            'name': _('Shipment Name'),
        }


#ItemFormSet = inlineformset_factory(Shipment, Item, form=ShipmentForm)