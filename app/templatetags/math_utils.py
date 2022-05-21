from django import template

register = template.Library()


@register.filter(name="abs")
def abs_value(value):
    value = remove_comma_separator(value)
    if not value:
        value = 0
    return format(abs(int(value)), ",d")


@register.filter(name="is_negative")
def is_negative(value):
    value = remove_comma_separator(value)
    return int(value) < 0


@register.filter(name="remove_comma_separator")
def remove_comma_separator(value):
    if isinstance(value, str):
        value = value.replace(",", "")
    return value
