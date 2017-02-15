from test_plus.test import TestCase
from .. import config

class test_config(TestCase):

    def test_dictionaries(self):
        """
        Dictionaries in python are call by reference. Ensure that new dictionaries are created each time.
        """
        json1 = config.product_base_json()
        json2 = config.product_base_json()
        json1['product']['title'] = 'hello'
        self.assertNotEqual(json1['product']['title'], json2['product']['title'])
