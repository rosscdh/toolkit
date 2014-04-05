# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Item

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug', 'status',)
    search_fields = ('name', 'slug',)
    list_filter = ['status']

admin.site.register(Item, ItemAdmin)
