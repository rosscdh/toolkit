# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import ReviewDocument


class ReviewDocumentAdmin(admin.ModelAdmin):
    list_display = ('slug', 'document',)
    #search_fields = ('name', 'slug', 'lawyer__first_name', 'lawyer__last_name')

    def queryset(self, request):
        return super(ReviewDocumentAdmin, self).queryset(request=request).select_related('document')


admin.site.register(ReviewDocument, ReviewDocumentAdmin)
