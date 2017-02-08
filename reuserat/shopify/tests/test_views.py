from django.test import RequestFactory

from test_plus.test import TestCase

from config.settings.common import SHOPIFY_APP_API_SECRET
from ..helpers import get_hmac
from ..views import *

import json


class BaseUserTestCase(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.factory = RequestFactory()
        # Simulate the json from shopify
        self.body = json.dumps({'updated_at': None, 'title': 'Example T-Shirt', 'published_at': '2017-02-07T18:37:51-05:00', 'id': 327475578523353102, 'handle': 'example-t-shirt', 'created_at': None, 'published_scope': 'global', 'images': [{'updated_at': None, 'product_id': 327475578523353102, 'created_at': None, 'id': 1234567, 'position': 0, 'src': '//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png', 'variant_ids': []}], 'body_html': None, 'vendor': 'Acme', 'variants': [{'updated_at': None, 'weight': 0.44, 'price': '19.99', 'created_at': None, 'grams': 200, 'option2': None, 'inventory_policy': 'deny', 'image_id': None, 'product_id': 327475578523353102, 'inventory_management': None, 'taxable': True, 'inventory_quantity': 75, 'compare_at_price': '24.99', 'title': '', 'id': 1234567, 'option1': 'Small', 'sku': 'example-shirt-s', 'option3': None, 'requires_shipping': True, 'position': 0, 'old_inventory_quantity': 75, 'fulfillment_service': 'manual', 'weight_unit': 'lb', 'barcode': None}, {'updated_at': None, 'weight': 0.44, 'price': '19.99', 'created_at': None, 'grams': 200, 'option2': None, 'inventory_policy': 'deny', 'image_id': None, 'product_id': 327475578523353102, 'inventory_management': 'shopify', 'taxable': True, 'inventory_quantity': 50, 'compare_at_price': '24.99', 'title': '', 'id': 1234568, 'option1': 'Medium', 'sku': 'example-shirt-m', 'option3': None, 'requires_shipping': True, 'position': 0, 'old_inventory_quantity': 50, 'fulfillment_service': 'manual', 'weight_unit': 'lb', 'barcode': None}], 'image': None, 'options': [{'name': 'Title', 'product_id': None, 'values': ['Small', 'Medium'], 'position': 1, 'id': 12345}], 'tags': 'mens t-shirt example', 'product_type': 'Shirts', 'template_suffix': None})


class TestOne(BaseUserTestCase):

    def test_get_redirect_url(self):
        # Instantiate the view directly. Never do this outside a test!
        # Generate a fake request
        body = get_hmac(self.body.encode(), SHOPIFY_APP_API_SECRET)  # Sign it with the secret key
        print(body)
        request = self.factory.post('/shopify/webhook/',
                                   data=body,
                                   content_type = 'application/json')


        body = request.body
        # Attach the user to the request



        # Attach the request to the view
        response = ShopifyWebhookBaseView.as_view()(request)
        print("\n RESPONSE: \n")
        print(response)
        # Expect: '/users/testuser/', as that is the default username for
        #   self.make_user()
       # self.assertEqual(
       #     view.get_redirect_url(),
       #     '/users/testuser/'
       # )
        self.assertEqual(1, 2)
