from test_plus.test import TestCase
from ..helpers import valid_sku

class TestReceiverGenericFunctions(TestCase):
    def test_valid_sku(self):
        sku = '123-456'
        self.assertTrue(valid_sku(sku))

    def test_invalid_sku(self):
        self.assertFalse(valid_sku('12345'))
        self.assertFalse(valid_sku('12345-'))
        self.assertFalse(valid_sku('abc-def'))
