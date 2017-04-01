from django import template


register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='slice_up_to')
def slice_up_to(value, num):
    """Use: {% for a in list|slice_to:num %}"""
    return value[0:num]


from django.contrib.humanize.templatetags.humanize import intcomma
@register.filter(name='currency')
def currency(dollars):
    dollars = round(float(dollars), 2)
    return "%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
