
from django.http.response import HttpResponse
from ..helpers import valid_sku
import shopify
import requests

from .config import product_base_json, product_create_url, shopify_intialize
from django.conf import settings


def create_product(sku, title):
    shopify_intialize()
    base_json = product_base_json()

    if not (title and sku):
        raise ValueError("Must provide sku and title, was given: sku- {}  title-{}".format(sku, title))

    if not valid_sku(sku):
        raise ValueError("SKU is invalid: {}".format(sku))

    # Must use JSON API instead of the python wrapper, because the wrapper doesn't  let you set the SKU until after you
    # save the item once, which messes up the webhooks which is listening for an SKU
    base_json['product']['title'] = title
    base_json['product']['variants'][0]['sku'] = sku

    response = requests.post(url=product_create_url,
                  json=base_json)

    if response.status_code != 201:
        return response.raise_for_status()

    id = response.json()['product']['id']

    product = shopify.Product.find(id)  # Turn the item into a ShopifyAPI active resource object.

    if product.errors:
        raise Exception(product.errors.full_messages())  # Maybe should make a new exception type?

    return product



