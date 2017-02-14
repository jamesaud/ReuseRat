
from django.http.response import HttpResponse
from ..helpers import valid_sku
import shopify
from urllib.parse import urljoin
from reuserat.shipments.models import Shipment
import requests
import os
import json
from .config import product_base_json, product_create_url, shop
from django.conf import settings

def create_product(sku, title):

    if not (title and sku):
        raise ValueError("Must provide sku and title, was given: sku- {}  title-{}".format(sku, title))

    if not valid_sku(sku):
        raise ValueError("SKU is invalid: {}".format(sku))

    product_base_json['product']['title'] = title
    product_base_json['product']['variants'][0]['sku'] = sku

    response = requests.post(url=product_create_url,
                  json=product_base_json
                  )

    if not (response.status_code == 201):
        return response.raise_for_status()

    id = response.json()['product']['id']

    product = shopify.Product.find(id)

    if product.errors:
        raise Exception(product.errors.full_messages())

    return product



def get_shopify_url(product_id):
    base_url = os.path.join("https://www.{}.com".format(settings.SHOPIFY_DOMAIN_NAME))
    return urljoin(base_url, os.path.join('admin', os.path.join('products', str(product_id))))
