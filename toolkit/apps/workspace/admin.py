from django.contrib import admin

from .models import Workspace, Tool

class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug', 'matter_code',)
    search_fields = ('name', 'slug',)

admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register([Tool])
