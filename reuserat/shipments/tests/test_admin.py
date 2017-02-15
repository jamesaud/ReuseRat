from test_plus.test import TestCase

from reuserat.shopify.tests.factories import ItemFactory
from .factories import ShipmentFactory
from .helpers import AdminHTMLParser
from ..admin import ShipmentAdmin
from ..models import Shipment




class TestMyUserCreationForm(TestCase):

    def setUp(self):
        self.shipment = ShipmentFactory()
        self.shipment_admin = ShipmentAdmin(model=Shipment, admin_site='test')


    def test_clean_username(self):
        """
        Test the html returned on the admin page of shipments for the related items
        """
        parser = AdminHTMLParser()

        # Instantiate the form with a new shipment
        html = self.shipment_admin.get_items(obj=self.shipment)
        parser.feed(html)
        tags = parser.tags

        # There should be only the header tags (counted by total open & close tags)
        self.assertEqual(tags['th'], 6)
        self.assertEqual(tags['table'], 2) # <table> + </table> = 2
        self.assertEqual(tags['tr'], 2)

        parser = AdminHTMLParser()
        # Add an item
        item = ItemFactory()
        item.shipment = self.shipment
        item.save()

        html = self.shipment_admin.get_items(obj=self.shipment)
        parser.feed(html)
        tags = parser.tags
        # Each shipment has 3 fields, so 6 td tags per shipment.
        self.assertEqual(tags['th'], 6)
        self.assertEqual(tags['td'], 6) # <table> + </table> = 2
        self.assertEqual(tags['table'], 2)
        self.assertEqual(tags['a'], 2)
        self.assertEqual(tags['tr'], 4)




