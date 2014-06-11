from django.contrib import admin
from toolkit.admin import SimpleTabularInline

from .models import Workspace, Tool, InviteKey
from toolkit.core.item.models import Item

class ItemInline(SimpleTabularInline):
    model = Item


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug', 'matter_code',)
    search_fields = ('name', 'slug',)
    inlines = [ItemInline, ]

admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register([Tool, InviteKey])
