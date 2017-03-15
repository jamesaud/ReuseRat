from django.conf import settings

def warehouse_address_to_html():
    return \
    """
    <li>{name}</li>
    <li>{line}</li>
    <li>{city}, {state}</li>
    <li>{zip}</li>
    """.format(
    name=settings.WAREHOUSE_NAME,
    line=settings.WAREHOUSE_ADDRESS_LINE,
    city=settings.WAREHOUSE_CITY,
    state=settings.WAREHOUSE_STATE,
    zip=settings.WAREHOUSE_ZIP)