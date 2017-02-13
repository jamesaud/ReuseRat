import re

def valid_sku(sku):
    if re.findall('[\d]+-[\d]+', sku):
        return True
    return False
