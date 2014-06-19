# -*- coding: utf-8 -*-
from django.contrib.comments.managers import CommentManager
from django.contrib.contenttypes.models import ContentType
from django.db import models

from jsonfield import JSONField
from rulez import registry as rulez_registry
from threadedcomments.models import ThreadedComment

from toolkit.apps.workspace.models import Workspace


class DiscussionComment(ThreadedComment, models.Model):
    subscribers = models.ManyToManyField('auth.User')
    is_archived = models.BooleanField(default=False)
    data = JSONField(default={})

    objects = CommentManager()

    def archive(self, is_archived=True):
        self.is_archived = is_archived
        self.save(update_fields=['is_archived'])
    archive.alters_data = True

    @property
    def matter(self):
        return self.content_object

    @matter.setter
    def matter(self, value):
        self.content_type_id = ContentType.objects.get_for_model(Workspace).pk
        self.object_pk = value.pk

    @property
    def participants(self):
        return set(self.subscribers.all() | self.matter.participants.all())

    def can_read(self, user):
        return user in self.participants

    def can_edit(self, user):
        return user in self.participants

    def can_delete(self, user):
        return user in self.participants

rulez_registry.register("can_read", DiscussionComment)
rulez_registry.register("can_edit", DiscussionComment)
rulez_registry.register("can_delete", DiscussionComment)
