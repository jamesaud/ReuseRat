from test_plus.test import TestCase
from ..models import Item
from reuserat.shipments.models import Shipment
from .factories import ItemFactory




class BaseModelTestCase(TestCase):

    def setUp(self):
        self.item = ItemFactory()



class TestSimple(BaseModelTestCase):

    def test_shopify_url(self):
        correct_url = 'https://www.reuserat.com/products/{}'.format(self.item.handle)
        url = self.item.get_shopify_url()
        self.assertEqual(correct_url, url)

