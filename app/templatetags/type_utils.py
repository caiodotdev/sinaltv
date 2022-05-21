from django import template

register = template.Library()

# This is never tested


@register.filter(name="is_dict")
def is_dict(value):
    return isinstance(value, dict)


@register.filter(name="to_d")
def is_dict(value):
    return isinstance(value, dict)