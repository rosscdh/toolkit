from django.contrib import admin

from toolkit.core.mixins import IsDeletedModelAdmin

from .models import EngagementLetter, Attachment


class EngagementLetterAdmin(IsDeletedModelAdmin, admin.ModelAdmin):
    list_display = ('__unicode__', 'slug', 'status', 'is_deleted')
    list_filter = ('status', 'is_deleted')
    search_fields = ('slug', 'id')


admin.site.register(EngagementLetter, EngagementLetterAdmin)
admin.site.register([Attachment])
