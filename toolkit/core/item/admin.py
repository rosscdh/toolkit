# -*- coding: utf-8 -*-
from django.contrib import admin
from toolkit.admin import SimpleTabularInline

from .models import Item
from toolkit.core.attachment.models import Revision


class RevisionInline(SimpleTabularInline):
    model = Revision


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug', 'status',)
    search_fields = ('name', 'slug',)
    list_filter = ['status']
    inlines = [RevisionInline, ]


admin.site.register(Item, ItemAdmin)
