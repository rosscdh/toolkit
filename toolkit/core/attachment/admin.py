# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Revision


class RevisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug', 'display_status',)
    search_fields = ('name', 'slug',)


admin.site.register(Revision, RevisionAdmin)
