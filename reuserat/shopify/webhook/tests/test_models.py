from test_plus.test import TestCase
from ..models import Item
from reuserat.shipments.models import Shipment
from .factories import ItemFactory
from config.settings.common import SHOPIFY_DOMAIN_NAME



class BaseModelTestCase(TestCase):

    def setUp(self):
        self.item = ItemFactory()



class TestItemModel(BaseModelTestCase):

    def test_shopify_url(self):
        correct_url = 'https://www.{}.com/products/{}'.format(SHOPIFY_DOMAIN_NAME, self.item.handle)
        url = self.item.get_shopify_url()

        self.assertEqual(correct_url, url)


