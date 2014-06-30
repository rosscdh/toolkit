# -*- coding: utf-8 -*-
from django.contrib import admin

from threadedcomments.admin import ThreadedCommentsAdmin
from threadedcomments.models import ThreadedComment

from .models import DiscussionComment


class DiscussionCommentsAdmin(ThreadedCommentsAdmin):
    pass

admin.site.register(DiscussionComment, DiscussionCommentsAdmin)
admin.site.unregister(ThreadedComment)
