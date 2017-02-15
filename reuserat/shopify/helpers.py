import re
from urllib.parse import urljoin
import os
from django.conf import settings


def valid_sku(sku):
    if re.findall('[\d]+-[\d]+', sku):
        return True
    return False


def get_shopify_admin_url(product_id):
    base_url = os.path.join("https://www.{}.com".format(settings.SHOPIFY_DOMAIN_NAME))
    return urljoin(base_url, os.path.join('admin', os.path.join('products', str(product_id))))


def get_shopify_product_url(product_id):
    return urljoin("https://www.{}.com".format(settings.SHOPIFY_DOMAIN_NAME), os.path.join('products', str(product_id)))
