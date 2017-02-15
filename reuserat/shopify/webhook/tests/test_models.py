from test_plus.test import TestCase

from config.settings.common import SHOPIFY_DOMAIN_NAME
from reuserat.shopify.tests.factories import ItemFactory


class BaseModelTestCase(TestCase):

    def setUp(self):
        self.item = ItemFactory()



class TestItemModel(BaseModelTestCase):

    def test_shopify_url(self):
        correct_url = 'https://www.{}.com/products/{}'.format(SHOPIFY_DOMAIN_NAME, self.item.id)
        url = self.item.get_shopify_url()

        self.assertEqual(correct_url, url)


