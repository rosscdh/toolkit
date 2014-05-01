# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import ReviewDocument


class ReviewDocumentAdmin(admin.ModelAdmin):
    list_display = ('slug', 'crocodoc_uuid', 'document',)
    search_fields = ('slug', 'crocodoc_uuid',)

    def queryset(self, request):
        return super(ReviewDocumentAdmin, self).queryset(request=request).select_related('document')


admin.site.register(ReviewDocument, ReviewDocumentAdmin)
