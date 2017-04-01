from test_plus.test import TestCase
from ..helpers import create_product

class test_helpers(TestCase):
    """
    It's difficult to test the ShopifyAPI without a test api server. We'll just test invalid function calls here.
    If 'Exception' is repalced in the create_product funtion, it should be updated here.
    """
    def test_create_product_raises_error(self):

        with self.assertRaises(Exception):
            create_product(sku=None, title=None)

        with self.assertRaises(Exception):
            create_product(sku=None, title='hello')

        with self.assertRaises(Exception):
            create_product(sku=12-23, title=None)
