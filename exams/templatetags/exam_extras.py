from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None


@register.filter
def attr(obj, attr_name):
    if obj and hasattr(obj, attr_name):
        return getattr(obj, attr_name)
    return ''