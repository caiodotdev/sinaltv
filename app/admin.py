#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.apps import apps
from django.contrib import admin

# Register your models here.

from app.models import *


def approve_selected(modeladmin, request, queryset):
    queryset.update(is_approved=True)


def desapprove_selected(modeladmin, request, queryset):
    queryset.update(is_approved=False)


approve_selected.short_description = "Aprovar itens selecionados"
desapprove_selected.short_description = "Desaprovar itens selecionados"


class ChannelInline(admin.TabularInline):
    model = Channel



class CategoryAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'id',
    )
    inlines = [ChannelInline]
    list_display = ("id", "name")

admin.site.register(Category, CategoryAdmin)


class ChannelAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'id',
    )
    inlines = []
    list_display = ("id", "title", "code", "image", "url", "category", "program_url")

admin.site.register(Channel, ChannelAdmin)
