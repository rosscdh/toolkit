from django.contrib import admin

from .models import EngagementLetter


class EngagementLetterAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'slug', 'status',)
    list_filter = ['status']
    search_fields = ('slug', 'id')


admin.site.register(EngagementLetter, EngagementLetterAdmin)
