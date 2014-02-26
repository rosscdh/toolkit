from django.contrib import admin

from toolkit.core.mixins import IsDeletedModelAdmin

from .models import EightyThreeB, Attachment


class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 1


class EightyThreeBAdmin(IsDeletedModelAdmin, admin.ModelAdmin):
    list_display = ('__unicode__', 'slug', 'status', 'is_deleted')
    list_filter = ('status', 'is_deleted')
    search_fields = ('slug', 'id')

    inlines = [
        AttachmentInline
    ]


admin.site.register(EightyThreeB, EightyThreeBAdmin)
admin.site.register([Attachment])
