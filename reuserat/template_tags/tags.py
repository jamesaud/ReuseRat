from django import template


register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='slice_up_to')
def slice_up_to(value, num):
    """Use: {% for a in list|slice_to:num %}"""
    return value[0:num]
