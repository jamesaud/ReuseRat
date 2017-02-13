import json

from django.test import RequestFactory
from test_plus.test import TestCase

from config.settings.common import SHOPIFY_WEBHOOK_API_KEY, SHOPIFY_APP_NAME
from reuserat.shipments.tests.factories import ShipmentFactory
from reuserat.shopify.webhook.helpers import get_hmac
from .factories import ItemFactory
from .. import receivers as r
from ..models import Item
from ..views import *


class BaseWebhookTestCase(TestCase):

    def setUp(self, body=None, topic=None):
        """
        topic: String, the shopify topic. checkout https://help.shopify.com/api/reference/webhook.
        body: Dict, the json body as a dictionary.
        """
        self.factory = RequestFactory()

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
        request.META['HTTP_X_SHOPIFY_HMAC_SHA256'] = get_hmac(body, SHOPIFY_WEBHOOK_API_KEY)
        request.META['HTTP_X_SHOPIFY_SHOP_DOMAIN'] = self.r_domain

        return ShopifyWebhookBaseView.as_view()(request)


class TestWebhook(BaseWebhookTestCase):

    def setUp(self):
        body = '{"id":327475578523353102,"title":"Example T-Shirt","body_html":null,"vendor":"Acme","product_type":"Shirts","created_at":null,"handle":"example-t-shirt","updated_at":null,"published_at":"2017-02-11T20:54:21-05:00","template_suffix":null,"published_scope":"global","tags":"mens t-shirt example","variants":[{"id":1234567,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-s","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":null,"option1":"Small","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":75,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":75,"requires_shipping":true},{"id":1234568,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-m","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":"shopify","option1":"Medium","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":50,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":50,"requires_shipping":true}],"options":[{"id":12345,"product_id":null,"name":"Title","position":1,"values":["Small","Medium"]}],"images":[{"id":1234567,"product_id":327475578523353100,"position":0,"created_at":null,"updated_at":null,"src":"//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png","variant_ids":[]}],"image":null}'
        body = json.loads(body)
        super(TestWebhook, self).setUp(body=body, topic="products/create")  # Set a valid topic name


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
        body = '{"id":327475578523353102,"title":"Example T-Shirt","body_html":null,"vendor":"Acme","product_type":"Shirts","created_at":null,"handle":"example-t-shirt","updated_at":null,"published_at":"2017-02-11T20:54:21-05:00","template_suffix":null,"published_scope":"global","tags":"mens t-shirt example","variants":[{"id":1234567,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-s","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":null,"option1":"Small","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":75,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":75,"requires_shipping":true},{"id":1234568,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-m","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":"shopify","option1":"Medium","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":50,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":50,"requires_shipping":true}],"options":[{"id":12345,"product_id":null,"name":"Title","position":1,"values":["Small","Medium"]}],"images":[{"id":1234567,"product_id":327475578523353100,"position":0,"created_at":null,"updated_at":null,"src":"//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png","variant_ids":[]}],"image":null}'
        self.body = json.loads(body)
        self.product_id = str(self.body['id'])
        self.shipment = ShipmentFactory()

        super(TestProductCreate, self).setUp(body=self.body, topic='products/create')

        self.set_sku(self.shipment.get_shipment_sku())


    def test_item_create(self):
        """
        When a webhook to product_create is sent, an item should be created.
        """
        response = self.send_request()

        item = Item.objects.get(pk=self.product_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(item.id, self.product_id)
        self.assertEqual(item.handle, self.body['handle'])
        self.assertEqual(item.name, self.body['title'])
        self.assertEqual(item.shipment.id, self.shipment.id)


    def test_invalid_sku(self):
        """
        When sku is invalid, an item should not be created.
        """
        self.set_sku('notvalidsku')
        response = self.send_request()
        self.assertFalse(Item.objects.filter(pk=self.product_id).exists())



class TestProductUpdate(BaseWebhookTestCase):

    def setUp(self):
        # Simulate shopify product/update json request.
        body = '{"id":327475578523353102,"title":"Example T-Shirt","body_html":null,"vendor":"Acme","product_type":"Shirts","created_at":null,"handle":"example-t-shirt","updated_at":null,"published_at":"2017-02-11T20:47:55-05:00","template_suffix":null,"published_scope":"global","tags":"mens t-shirt example","variants":[{"id":1234567,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-s","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":null,"option1":"Small","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":75,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":75,"requires_shipping":true},{"id":1234568,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-m","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":"shopify","option1":"Medium","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":50,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":50,"requires_shipping":true}],"options":[{"id":12345,"product_id":null,"name":"Title","position":1,"values":["Small","Medium"]}],"images":[{"id":1234567,"product_id":327475578523353100,"position":0,"created_at":null,"updated_at":null,"src":"//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png","variant_ids":[]}],"image":null}'
        self.body = json.loads(body)
        self.item = ItemFactory()                                                             # Create a shipment.
        self.body['id'] = self.item.id
        super(TestProductUpdate, self).setUp(body=self.body, topic='products/update')   # Set up the update request
        self.set_sku(self.item.shipment.get_shipment_sku())   # Update the sku

    def test_item_update(self):
        response = self.send_request()
        item = Item.objects.get(pk=self.item.id)

        self.assertEqual(item.handle, self.body['handle'])
        self.assertEqual(item.name, self.body['title'])

    def test_item_failed_update(self):
        self.body['id'] = 2345
        response = self.send_request()
        with self.assertRaises(Item.DoesNotExist):
           Item.objects.get(pk=self.body['id'])



class TestProductDelete(BaseWebhookTestCase):
    def setUp(self):
        # Simulate shopify product/delete json request.
        body = '{"id":327475578523353102,"title":"Example T-Shirt","body_html":null,"vendor":"Acme","product_type":"Shirts","created_at":null,"handle":"example-t-shirt","updated_at":null,"published_at":"2017-02-11T20:47:55-05:00","template_suffix":null,"published_scope":"global","tags":"mens t-shirt example","variants":[{"id":1234567,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-s","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":null,"option1":"Small","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":75,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":75,"requires_shipping":true},{"id":1234568,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-m","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":"shopify","option1":"Medium","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":50,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":50,"requires_shipping":true}],"options":[{"id":12345,"product_id":null,"name":"Title","position":1,"values":["Small","Medium"]}],"images":[{"id":1234567,"product_id":327475578523353100,"position":0,"created_at":null,"updated_at":null,"src":"//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png","variant_ids":[]}],"image":null}'
        self.body = json.loads(body)
        self.item = ItemFactory()  # Create a shipment.
        self.body['id'] = self.item.id
        super(TestProductDelete, self).setUp(body=self.body, topic='products/delete')  # Set up the update request
        self.set_sku(self.item.shipment.get_shipment_sku())  # Update the sku

    def test_item_delete(self):
        self.assertTrue(Item.objects.filter(pk=self.item.id).exists())   # Item should exist
        response = self.send_request()
        self.assertFalse(Item.objects.filter(pk=self.item.id).exists())


