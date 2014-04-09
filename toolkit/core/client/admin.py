# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Client


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'lawyer')
    search_fields = ('name', 'slug', 'lawyer__first_name', 'lawyer__last_name')

    def queryset(self, request):
        return super(ClientAdmin, self).queryset(request=request).select_related('lawyer')


admin.site.register(Client, ClientAdmin)


