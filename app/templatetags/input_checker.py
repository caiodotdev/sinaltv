#! -*- coding: UTF-8 -*-
"""
Set of template tags to determine input nature
"""
from django import template
register = template.Library()


@register.filter(name="is_select_multiple")
def is_select_multiple(field):
    """
    Template tag to check if input is select
    :param field: Input field
    :return: True if is select, False if not
    """
    return "SelectMultiple" in field.field.widget.__class__.__name__


@register.filter(name="is_select")
def is_select(field):
    """
    Template tag to check if input is select
    :param field: Input field
    :return: True if is select, False if not
    """
    return "Select" in field.field.widget.__class__.__name__


@register.filter(name="is_checkbox")
def is_checkbox(field):
    """
    Template tag to check if input is checkbox
    :param field: Input field
    :return: True if is checkbox, False if not
    """
    return field.field.widget.__class__.__name__ == "CheckboxInput"


@register.filter('is_datetime')
def is_datetime(input):
    """
    Template tag to check if input is Datetime
    :param input: Input field
    :return: True if is datetime, False if not
    """
    return input.field.widget.__class__.__name__ == "DateTimeInput"


@register.filter('is_file')
def is_file(input):
    """
    Template tag to check if input is file
    :param input:  Input field
    :return: True if  is file, False if not
    """
    return input.field.widget.__class__.__name__ == "ClearableFileInput"\


@register.filter('is_text_area')
def is_text_area(input):
    """
    Template tag to check if input is file
    :param input:  Input field
    :return: True if  is file, False if not
    """
    return input.field.widget.__class__.__name__ == "Textarea"
