#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
Global variables for base module
"""
from django.utils.translation import ugettext_lazy as _
from django.conf import LazySettings

settings = LazySettings()


def get_from_settings_or_default(var_name, default):
    try:
        return settings.__getattr__(var_name)
    except AttributeError:
        return default


# Items by page on paginator views
ITEMS_BY_PAGE = 10

CREATE_SUFFIX = "_create"
LIST_SUFFIX = "_list"
DETAIL_SUFFIX = "_detail"
UPDATE_SUFFIX = "_update"
DELETE_SUFFIX = "_delete"

API_SUFFIX = "_api"
style = "base_django/flexbox"


# Messages
OBJECT_CREATED_SUCCESSFULLY = _("Object created successfully")
OBJECT_UPDATED_SUCCESSFULLY = _("Object updated successfully")
OBJECT_DELETED_SUCCESSFULLY = _("Object deleted successfully")

BASE_MODELS_TRANSLATION_NAME = _("Name")
BASE_MODELS_TRANSLATION_DESCRIPTION = _("Description")
BASE_MODELS_TRANSLATION_SLUG = _("Slug")
BASE_MODELS_TRANSLATION_CREATED = _("Created")
BASE_MODELS_TRANSLATION_MODIFIED = _("Modified")
BASE_MODELS_TRANSLATION_ACTIVE = _("Active")

CONFIGURING_APPLICATION = _("Configuring application {}")
CREATING_PERMISSION_WITH_NAME = _("Creating Permission with name {}")
CREATING_GROUP_WITH_NAME = _("Creating Group with name {}")


CATEGORY_PREFIX = "CATEGORY"

CATEGORY_VERBOSE_NAME = _("Category")
CATEGORY_VERBOSE_NAME_PLURAL = _("Category")

CATEGORY_LIST_URL_NAME = CATEGORY_PREFIX + LIST_SUFFIX
CATEGORY_CREATE_URL_NAME = CATEGORY_PREFIX + CREATE_SUFFIX
CATEGORY_DETAIL_URL_NAME = CATEGORY_PREFIX + DETAIL_SUFFIX
CATEGORY_UPDATE_URL_NAME = CATEGORY_PREFIX + UPDATE_SUFFIX
CATEGORY_DELETE_URL_NAME = CATEGORY_PREFIX + DELETE_SUFFIX
CATEGORY_LIST_JSON_URL_NAME = CATEGORY_PREFIX + '_list_json'


CHANNEL_PREFIX = "CHANNEL"

CHANNEL_VERBOSE_NAME = _("Channel")
CHANNEL_VERBOSE_NAME_PLURAL = _("Channel")

CHANNEL_LIST_URL_NAME = CHANNEL_PREFIX + LIST_SUFFIX
CHANNEL_CREATE_URL_NAME = CHANNEL_PREFIX + CREATE_SUFFIX
CHANNEL_DETAIL_URL_NAME = CHANNEL_PREFIX + DETAIL_SUFFIX
CHANNEL_UPDATE_URL_NAME = CHANNEL_PREFIX + UPDATE_SUFFIX
CHANNEL_DELETE_URL_NAME = CHANNEL_PREFIX + DELETE_SUFFIX
CHANNEL_LIST_JSON_URL_NAME = CHANNEL_PREFIX + '_list_json'

