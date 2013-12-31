from django.contrib import admin

from .models import EightyThreeB, Attachment


class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 1


class EightyThreeBAdmin(admin.ModelAdmin):
    inlines = [
        AttachmentInline
    ]


admin.site.register(EightyThreeB, EightyThreeBAdmin)
admin.site.register([Attachment])
