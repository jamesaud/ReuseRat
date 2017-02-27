from django.conf import settings
import shopify
import os




### SHOPIFY SETTINGS ###
SHOPIFY_SHOP_URL = "https://{api_key}:{password}@{shop_name}/admin/".format(api_key=settings.SHOPIFY_API_KEY,
                                                                   password=settings.SHOPIFY_PASSWORD,
                                                                   shop_name=settings.SHOPIFY_APP_NAME)

def shopify_intialize():
    shopify.ShopifyResource.set_site(SHOPIFY_SHOP_URL)
    shop = shopify.Shop.current()


### SHOPIFY URL ENDPOINTS ###
product_create_url = os.path.join(SHOPIFY_SHOP_URL, 'products.json/')


### SHOPIFY JSON REQUEST TEMPLATES ###
# Wrap json dictionaries in lambda to prevent referencing the same dictionary accidently.

product_base_json = lambda: {
  "product": {
    "title": None,  # Replace this with the real product title, as it is required.
    "published": False,
      "variants": [
      {
        "sku": None,    # Replace with the sku, as we are requiring it.
        "inventory_management": "shopify",
        "inventory_quantity": 1,
      },
    ]
  }
}

