from django.contrib import admin
from toolkit.admin import SimpleTabularInline

from .models import Workspace, WorkspaceParticipants, Tool, InviteKey
from toolkit.core.item.models import Item

class ItemInline(SimpleTabularInline):
    model = Item


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug', 'matter_code',)
    search_fields = ('name', 'slug',)
    inlines = [ItemInline, ]


class WorkspaceParticipantsAdmin(admin.ModelAdmin):
    list_display = ('workspace', 'user', 'role')
    list_filter = ['is_matter_owner', 'role']
    search_fields = ('workspace__name', 'user__first_name', 'user__last_name', 'user__email')

    def get_queryset(self, request):
        return super(WorkspaceParticipantsAdmin, self).get_queryset(request=request).filter(workspace__is_deleted=False).select_related('workspace', 'user').order_by('role')


admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(WorkspaceParticipants, WorkspaceParticipantsAdmin)

admin.site.register([Tool, InviteKey])
