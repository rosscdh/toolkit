from django.contrib import admin

from .models import Workspace, Tool


admin.site.register([Workspace, Tool])
