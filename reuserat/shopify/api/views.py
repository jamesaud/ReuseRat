
API_KEY = '73955c3af881dbe798a018d6f59d5c1e'
PASSWORD = '708074521e0e66953480f2e2645e6a81'
from config.settings.common import SHOPIFY_APP_NAME
from django.http.response import HttpResponse

from .helpers import create_product
import shopify



def shopify_test(request):

    shop_url = "https://{api_key}:{password}@{shop_name}/admin".format(api_key=API_KEY,
                                                                       password=PASSWORD,
                                                                       shop_name=SHOPIFY_APP_NAME)
    new_product = create_product(sku='12-32', title='My Product')
    return HttpResponse("created")
