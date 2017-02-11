from django.test import RequestFactory

from test_plus.test import TestCase

from config.settings.common import SHOPIFY_APP_API_SECRET, SHOPIFY_APP_NAME
from reuserat.shipments.tests.factories import ShipmentFactory
from ..helpers import get_hmac
from ..views import *
from .. import receivers as r

from ..models import Item
import json
from django.core.exceptions import ObjectDoesNotExist


class BaseWebhookTestCase(TestCase):

    def setUp(self, body=None, topic=None):
        """
        topic: checkout https://help.shopify.com/api/reference/webhook.
        """
        self.factory = RequestFactory()
        self.shipment = ShipmentFactory()

        # Simulate the json from shopify, copied from a shopify product_create request.
        if not body:
            body = {'updated_at': None, 'title': 'Example T-Shirt', 'published_at': '2017-02-07T18:37:51-05:00', 'id': 327475578523353102, 'handle': 'example-t-shirt', 'created_at': None, 'published_scope': 'global', 'images': [{'updated_at': None, 'product_id': 327475578523353102, 'created_at': None, 'id': 1234567, 'position': 0, 'src': '//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png', 'variant_ids': []}], 'body_html': None, 'vendor': 'Acme', 'variants': [{'updated_at': None, 'weight': 0.44, 'price': '19.99', 'created_at': None, 'grams': 200, 'option2': None, 'inventory_policy': 'deny', 'image_id': None, 'product_id': 327475578523353102, 'inventory_management': None, 'taxable': True, 'inventory_quantity': 75, 'compare_at_price': '24.99', 'title': '', 'id': 1234567, 'option1': 'Small', 'sku': 'example-shirt-s', 'option3': None, 'requires_shipping': True, 'position': 0, 'old_inventory_quantity': 75, 'fulfillment_service': 'manual', 'weight_unit': 'lb', 'barcode': None}, {'updated_at': None, 'weight': 0.44, 'price': '19.99', 'created_at': None, 'grams': 200, 'option2': None, 'inventory_policy': 'deny', 'image_id': None, 'product_id': 327475578523353102, 'inventory_management': 'shopify', 'taxable': True, 'inventory_quantity': 50, 'compare_at_price': '24.99', 'title': '', 'id': 1234568, 'option1': 'Medium', 'sku': 'example-shirt-m', 'option3': None, 'requires_shipping': True, 'position': 0, 'old_inventory_quantity': 50, 'fulfillment_service': 'manual', 'weight_unit': 'lb', 'barcode': None}], 'image': None, 'options': [{'name': 'Title', 'product_id': None, 'values': ['Small', 'Medium'], 'position': 1, 'id': 12345}], 'tags': 'mens t-shirt example', 'product_type': 'Shirts', 'template_suffix': None}
        body['variants'][0]['sku'] = self.shipment.get_shipment_sku()  # set the sku to be associate with this test shipment

        # Simulate Shopify Request
        if not topic:
            topic = "products/create"   # Set a valid signal name

        # Prefix with 'r', for 'request'
        self.r_body = body
        self.r_topic = topic
        self.r_domain = SHOPIFY_APP_NAME


    def set_request_topic(self, topic):
        self.r_topic = topic


    def set_sku(self, sku):
        self.r_body['variants'][0]['sku'] = sku


    def send_request(self):
        body = json.dumps(self.r_body).encode()

        request = self.factory.post('/shopify/webhook/',
                                    data=body,
                                    content_type='application/json')

        request.META['HTTP_X_SHOPIFY_TOPIC'] = self.r_topic
        request.META['HTTP_X_SHOPIFY_HMAC_SHA256'] = get_hmac(body, SHOPIFY_APP_API_SECRET)
        request.META['HTTP_X_SHOPIFY_SHOP_DOMAIN'] = self.r_domain

        return ShopifyWebhookBaseView.as_view()(request)


class TestWebhook(BaseWebhookTestCase):

    def test_webhook(self):
        """
        Verify that receiving shopify webook works. This test simulates the request that would come from shopify.
        """

        # Instantiate the view directly. Never do this outside a test!
        response = self.send_request()

        self.assertEqual(response.status_code, 200)


class TestReceiverGenericFunctions(TestCase):
    def test_valid_sku(self):
        sku = '123-456'
        self.assertTrue(r.valid_sku(sku))

    def test_invalid_sku(self):
        self.assertFalse(r.valid_sku('12345'))
        self.assertFalse(r.valid_sku('12345-'))
        self.assertFalse(r.valid_sku('abc-def'))


class TestProductCreate(BaseWebhookTestCase):

    def setUp(self):
        self.product_id = '327475578523353102'
        body = {'id': self.product_id, 'updated_at': None, 'title': 'Example T-Shirt', 'published_at': '2017-02-07T18:37:51-05:00', 'handle': 'example-t-shirt', 'created_at': None, 'published_scope': 'global', 'images': [{'updated_at': None, 'product_id': 327475578523353102, 'created_at': None, 'id': 1234567, 'position': 0, 'src': '//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png', 'variant_ids': []}], 'body_html': None, 'vendor': 'Acme', 'variants': [{'updated_at': None, 'weight': 0.44, 'price': '19.99', 'created_at': None, 'grams': 200, 'option2': None, 'inventory_policy': 'deny', 'image_id': None, 'product_id': 327475578523353102, 'inventory_management': None, 'taxable': True, 'inventory_quantity': 75, 'compare_at_price': '24.99', 'title': '', 'id': 1234567, 'option1': 'Small', 'sku': 'example-shirt-s', 'option3': None, 'requires_shipping': True, 'position': 0, 'old_inventory_quantity': 75, 'fulfillment_service': 'manual', 'weight_unit': 'lb', 'barcode': None}, {'updated_at': None, 'weight': 0.44, 'price': '19.99', 'created_at': None, 'grams': 200, 'option2': None, 'inventory_policy': 'deny', 'image_id': None, 'product_id': 327475578523353102, 'inventory_management': 'shopify', 'taxable': True, 'inventory_quantity': 50, 'compare_at_price': '24.99', 'title': '', 'id': 1234568, 'option1': 'Medium', 'sku': 'example-shirt-m', 'option3': None, 'requires_shipping': True, 'position': 0, 'old_inventory_quantity': 50, 'fulfillment_service': 'manual', 'weight_unit': 'lb', 'barcode': None}], 'image': None, 'options': [{'name': 'Title', 'product_id': None, 'values': ['Small', 'Medium'], 'position': 1, 'id': 12345}], 'tags': 'mens t-shirt example', 'product_type': 'Shirts', 'template_suffix': None}
        super(TestProductCreate, self).setUp(body=body, topic='products/create')


    def test_item_create(self):
        """
        When a webhook to product_create is sent, an item should be created.
        """
        self.response = self.send_request()

        item = Item.objects.get(pk=self.product_id)

        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(item.id, self.product_id)
        self.assertEqual(item.shipment.id, self.shipment.id)


    def test_invalid_sku(self):
        self.set_sku('notvalidsku')
        self.response = self.send_request()

        try:
            Item.objects.get(pk=self.product_id)
        except Item.DoesNotExist:
            self.assertTrue(True)       # Item should not be created when sku is invalid
        else:
            self.assertTrue(False)



