
API_KEY = '73955c3af881dbe798a018d6f59d5c1e'
PASSWORD = '708074521e0e66953480f2e2645e6a81'
from config.settings.common import SHOPIFY_APP_NAME
from django.http.response import HttpResponse
from ..helpers import valid_sku
import shopify


shop_url = "https://{api_key}:{password}@{shop_name}/admin".format(api_key=API_KEY,
                                                                   password=PASSWORD,
                                                                   shop_name=SHOPIFY_APP_NAME)
shopify.ShopifyResource.set_site(shop_url)
shop = shopify.Shop.current()



def create_product(sku, title):

    if not (title and sku):
        raise ValueError("Must provide sku and title, was given: sku- {}  title-{}".format(sku, title))

    if not valid_sku(sku):
        raise ValueError("SKU is invalid: {}".format(sku))



    # Create new product
    new_product = shopify.Product()
    new_product.title = title
    new_product.published_at = None
    new_product.save()

    variant = new_product.attributes['variants'][0]
    variant.attributes['sku'] = sku
    variant.attributes["inventory_management"] = "shopify"
    variant.attributes["inventory_quantity"] = 1
    new_product.save()

    if new_product.errors:
        raise Exception(new_product.errors.full_messages())

    return new_product

