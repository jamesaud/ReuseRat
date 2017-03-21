import json

from django.test import RequestFactory
from test_plus.test import TestCase
from reuserat.shopify.models import Status
from config.settings.common import SHOPIFY_WEBHOOK_API_KEY, SHOPIFY_APP_NAME
from reuserat.shipments.tests.factories import ShipmentFactory
from reuserat.shopify.tests.factories import ItemFactory,ItemOrderDetailsFactory
from reuserat.shopify.webhook.helpers import get_hmac
from .. import receivers as r
from ..views import *
from ...models import Item
from reuserat.stripe.helpers import create_charge


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



class TestProductCreate(BaseWebhookTestCase):

    def setUp(self):
        body = '{"id":327475578523353102,"title":"Example T-Shirt","body_html":null,"vendor":"Acme","product_type":"Shirts","created_at":null,"handle":"example-t-shirt","updated_at":null,"published_at":"2017-02-11T20:54:21-05:00","template_suffix":null,"published_scope":"global","tags":"mens t-shirt example","variants":[{"id":1234567,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-s","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":null,"option1":"Small","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":75,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":75,"requires_shipping":true},{"id":1234568,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-m","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":"shopify","option1":"Medium","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":50,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":50,"requires_shipping":true}],"options":[{"id":12345,"product_id":null,"name":"Title","position":1,"values":["Small","Medium"]}],"images":[{"id":1234567,"product_id":327475578523353100,"position":0,"created_at":null,"updated_at":null,"src":"//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png","variant_ids":[]}],"image":null}'
        self.body = json.loads(body)
        self.body['published_at'] = False  # Make it unpublished
        self.product_id = str(self.body['variants'][0]['product_id'])
        self.shipment = ShipmentFactory()
        super(TestProductCreate, self).setUp(body=self.body, topic='products/create')

        self.set_sku(self.shipment.get_shipment_sku())


    def test_item_create(self):
        from django.db import transaction

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
        self.assertEqual(item.is_visible, False)   # Should be unpublished.

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
        self.item = ItemFactory()

        self.body['variants'][0]['product_id'] = self.item.id
        super(TestProductUpdate, self).setUp(body=self.body, topic='products/update')   # Set up the update request
        self.set_sku(self.item.shipment.get_shipment_sku())   # Update the sku

    def test_item_update(self):
        response = self.send_request()
        item = Item.objects.get(pk=self.item.id)

        self.assertEqual(item.handle, self.body['handle'])
        self.assertEqual(item.name, self.body['title'])
        self.assertEqual(item.is_visible, True)


    def test_item_update_or_create(self):
        # Item should be created if it is not updated.
        product_id = self.body['variants'][0]['product_id'] = 2345
        response = self.send_request()
        self.assertTrue(Item.objects.filter(pk=product_id).exists())


class TestProductDelete(BaseWebhookTestCase):
    def setUp(self):
        # Simulate shopify product/delete json request.
        body = '{"id":327475578523353102,"title":"Example T-Shirt","body_html":null,"vendor":"Acme","product_type":"Shirts","created_at":null,"handle":"example-t-shirt","updated_at":null,"published_at":"2017-02-11T20:47:55-05:00","template_suffix":null,"published_scope":"global","tags":"mens t-shirt example","variants":[{"id":1234567,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-s","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":null,"option1":"Small","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":75,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":75,"requires_shipping":true},{"id":1234568,"product_id":327475578523353100,"title":"","price":"19.99","sku":"example-shirt-m","position":0,"grams":200,"inventory_policy":"deny","compare_at_price":"24.99","fulfillment_service":"manual","inventory_management":"shopify","option1":"Medium","option2":null,"option3":null,"created_at":null,"updated_at":null,"taxable":true,"barcode":null,"image_id":null,"inventory_quantity":50,"weight":0.44,"weight_unit":"lb","old_inventory_quantity":50,"requires_shipping":true}],"options":[{"id":12345,"product_id":null,"name":"Title","position":1,"values":["Small","Medium"]}],"images":[{"id":1234567,"product_id":327475578523353100,"position":0,"created_at":null,"updated_at":null,"src":"//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png","variant_ids":[]}],"image":null}'
        self.body = json.loads(body)
        self.item = ItemFactory()  # Create a shipment.
        self.body['variants'][0]['product_id'] = self.item.id
        super(TestProductDelete, self).setUp(body=self.body, topic='products/delete')  # Set up the update request
        self.set_sku(self.item.shipment.get_shipment_sku())  # Update the sku

    def test_item_delete(self):
        self.assertTrue(Item.objects.filter(pk=self.item.id).exists())   # Item should exist
        response = self.send_request()
        self.assertFalse(Item.objects.filter(pk=self.item.id).exists())

class TestOrderOrderReceiver(BaseWebhookTestCase):

    def setUp(self):
         # simulate shopify order received json request
        body = '{"id":4869750532,"email":"jj@jj.com","closed_at":null,"created_at":"2017-03-04T16:50:26-05:00","updated_at":"2017-03-04T16:50:26-05:00","number":3,"note":"","token":"7b3edb00e35755881daae9701a0c7015","gateway":"manual","test":false,"total_price":"1.07","subtotal_price":"1.00","total_weight":454,"total_tax":"0.07","taxes_included":false,"currency":"USD","financial_status":"paid","confirmed":true,"total_discounts":"0.00","total_line_items_price":"1.00","cart_token":null,"buyer_accepts_marketing":false,"name":"#1003","referring_site":null,"landing_site":null,"cancelled_at":null,"cancel_reason":null,"total_price_usd":"1.07","checkout_token":null,"reference":null,"user_id":112270404,"location_id":21386820,"source_identifier":null,"source_url":null,"processed_at":"2017-03-04T16:50:26-05:00","device_id":null,"browser_ip":null,"landing_site_ref":null,"order_number":1003,"discount_codes":[],"note_attributes":[],"payment_gateway_names":["manual"],"processing_method":"manual","checkout_id":null,"source_name":"shopify_draft_order","fulfillment_status":null,"tax_lines":[{"title":"IN State Tax","price":"0.07","rate":0.07}],"tags":"","contact_email":null,"order_status_url":null,"line_items":[{"id":9473954756,"variant_id":36372184260,"title":"testest","quantity":1,"price":"1.00","grams":454,"sku":"9-4","variant_title":null,"vendor":"ReuseRat","fulfillment_service":"manual","product_id":10013286724,"requires_shipping":true,"taxable":true,"gift_card":false,"name":"testest","variant_inventory_management":"shopify","properties":[],"product_exists":true,"fulfillable_quantity":1,"total_discount":"0.00","fulfillment_status":null,"tax_lines":[{"title":"IN State Tax","price":"0.07","rate":0.07}]}],"shipping_lines":[],"fulfillments":[],"refunds":[]}'
        self.body = json.loads(body)
        item_list = self.body['line_items']
        self.item=ItemFactory()
        self.itemOrderDetails = ItemOrderDetailsFactory()
        self.item.id = body['product_id']
        super(TestOrderOrderReceiver, self).setUp(body=self.body, topic='orders/paid')  # Set up the update request

        def test_order_payment(self):
            response = self.send_request()
            self.assertTrue(Item.objects.get(pk=self.item.id).exists())
            item_object_created =Item.objects.get(pk=self.item.id)
            self.assertEqual(item_object_created.status, Status.SOLD)
            self.assertTrue(item_object_created.itemorderdetails.order_data)
            self.assertTrue(item_object_created.itemorderdetails.order_data)
            self.assertTrue(item_object_created.itemorderdetails.charge_id)


