import json

from django.test import RequestFactory
from test_plus.test import TestCase
from reuserat.users.tests.factories import UserFactory
from reuserat.shipments.tests.factories import ShipmentFactory
from reuserat.shopify.models import Status
from reuserat.shopify.tests.factories import ItemFactory, ItemOrderDetailsFactory
from reuserat.shopify.webhook.helpers import get_hmac
from reuserat.stripe.helpers import cents_to_dollars, dollars_to_cents
from reuserat.stripe.models import TransactionPaymentTypeChoices, TransactionTypeChoices
from ..views import *
from ...models import Item


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
        self.r_domain = settings.SHOPIFY_APP_NAME


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
        request.META['HTTP_X_SHOPIFY_HMAC_SHA256'] = get_hmac(body, settings.SHOPIFY_WEBHOOK_API_KEY)
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
        body = '{"id": 788032119674292900}'
        self.body = json.loads(body)
        self.item = ItemFactory()  # Create a shipment.
        self.body['id'] = self.item.id
        super(TestProductDelete, self).setUp(body=self.body, topic='products/delete')  # Set up the update request

    def test_item_delete(self):
        self.assertTrue(Item.objects.filter(pk=self.item.id).exists())   # Item should exist
        response = self.send_request()
        self.assertFalse(Item.objects.filter(pk=self.item.id).exists())



class TestFulfillmentsReceiver(BaseWebhookTestCase):

    def setUp(self):
        body = '{"id":123456,"order_id":820982911946154500,"status":"pending","created_at":"2017-07-10T13:09:15-04:00","service":null,"updated_at":"2017-07-10T13:09:15-04:00","tracking_company":"UPS","shipment_status":null,"email":"jon@doe.ca","destination":{"first_name":"Steve","address1":"123 Shipping Street","phone":"555-555-SHIP","city":"Shippington","zip":"K2P0S0","province":"Kentucky","country":"United States","last_name":"Shipper","address2":null,"company":"Shipping Company","latitude":null,"longitude":null,"name":"Steve Shipper","country_code":"US","province_code":"KY"},"tracking_number":"1z827wk74630","tracking_numbers":["1z827wk74630"],"tracking_url":"http://wwwapps.ups.com/etracking/tracking.cgi?InquiryNumber1=1z827wk74630&TypeOfInquiryNumber=T&AcceptUPSLicenseAgreement=yes&submit=Track","tracking_urls":["http://wwwapps.ups.com/etracking/tracking.cgi?InquiryNumber1=1z827wk74630&TypeOfInquiryNumber=T&AcceptUPSLicenseAgreement=yes&submit=Track"],"receipt":{},"line_items":[{"id":866550311766439000,"variant_id":null,"title":"Apples to Apples Junior!","quantity":1,"price":"5.00","grams":680,"sku":"A353","variant_title":null,"vendor":null,"fulfillment_service":"manual","product_id":10083851844,"requires_shipping":true,"taxable":true,"gift_card":false,"name":"Apples to Apples Junior!","variant_inventory_management":null,"properties":[],"product_exists":true,"fulfillable_quantity":1,"total_discount":"0.00","fulfillment_status":null,"tax_lines":[]},{"id":141249953214522980,"variant_id":null,"title":"Legacy Of Love Sisters Figurine by Kim Lawrence. Gregg Gift Company","quantity":1,"price":"7.99","grams":1451,"sku":"32-22","variant_title":null,"vendor":null,"fulfillment_service":"manual","product_id":11360551364,"requires_shipping":true,"taxable":true,"gift_card":false,"name":"Legacy Of Love Sisters Figurine by Kim Lawrence. Gregg Gift Company","variant_inventory_management":null,"properties":[],"product_exists":true,"fulfillable_quantity":1,"total_discount":"5.00","fulfillment_status":null,"tax_lines":[]}]}'
        self.body = json.loads(body)

        self.item_price = float(self.body['line_items'][0]['price'])
        print(self.item_price)
        # Create an item in our database, set the user to the shipment
        self.user = UserFactory()
        self.item = ItemFactory(name=self.body['line_items'][0]['name'])
        self.item.id = self.body['line_items'][0]['product_id']
        self.item.save()
        self.item.shipment.user = self.user
        self.item.shipment.save()

        # Set up the webhook with the correct call
        super().setUp(body=self.body, topic='fulfillments/create')


    def test_payment_to_user(self):
        """Calls Stripe API"""
        old_balance = self.user.get_current_balance()

        response = self.send_request()

        new_balance = self.user.get_current_balance()

        print(old_balance, new_balance)
        # Make sure the user was paid the correct amount of Stripe
        self.assertEqual(old_balance, new_balance - (self.item_price * settings.SPLIT_PERCENT_PER_SALE))

        # Test the Item object
        item = Item.objects.get(pk=self.item.id)
        balance_in_cents = self.user.stripe_account.retrieve_balance()
        balance_in_dollars = cents_to_dollars(balance_in_cents)
        self.assertEqual(item.status, Status.SOLD)
        self.assertIsNotNone(item.itemorderdetails.order_data)
        self.assertIsNotNone(item.itemorderdetails.transfer_id)

        # Test that the Stripe transfer was successful
        self.assertEqual(dollars_to_cents(float(self.body['line_items'][0]['price'])) * settings.SPLIT_PERCENT_PER_SALE,
                         self.user.stripe_account.retrieve_balance())

        # Test the transaction object that should be created
        transaction = self.user.transaction_set.first()
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, balance_in_dollars)
        self.assertEqual(TransactionPaymentTypeChoices.ITEM_SOLD, transaction.payment_type)
        self.assertEqual(TransactionTypeChoices.IN, transaction.type)
        self.assertEqual(transaction.message, 'Paid for selling the item: ' + self.body['line_items'][0]['name'])

        #  We can check and make sure the funds should not be added to a user's account if request comes a second time.
        old_balance = self.user.get_current_balance()
        self.send_request()
        new_balance = self.user.get_current_balance() # Should be the same as current balance
        self.assertEqual(old_balance, new_balance)  # Don't pay the user twice if we already heard a fulfillment webhook.



