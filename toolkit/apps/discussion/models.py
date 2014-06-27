# -*- coding: utf-8 -*-
from django.contrib.comments.managers import CommentManager
from django.contrib.contenttypes.models import ContentType
from django.db import models

from jsonfield import JSONField
from rulez import registry as rulez_registry
from threadedcomments.models import ThreadedComment
from uuidfield import UUIDField

from toolkit.apps.workspace.models import Workspace


class DiscussionComment(ThreadedComment, models.Model):
    slug = UUIDField(auto=True, db_index=True)
    participants = models.ManyToManyField('auth.User')
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

    def can_read(self, user):
        if self.parent_id:
            return user in DiscussionComment.objects.get(pk=self.parent_id).participants.all()
        return user in self.participants.all()

    def can_edit(self, user):
        return user == self.user

    def can_delete(self, user):
        if self.parent_id:
            return False
        return user == self.user

rulez_registry.register("can_read", DiscussionComment)
rulez_registry.register("can_edit", DiscussionComment)
rulez_registry.register("can_delete", DiscussionComment)


"""
Add our api permission handler methods to the DiscussionComment.participants model.
"""
def participant_can_edit(self, user, **kwargs):
    return user == self.user

def participant_can_delete(self, user, **kwargs):
    return user == self.user

DiscussionComment.participants.through.add_to_class('can_edit', participant_can_edit)
DiscussionComment.participants.through.add_to_class('can_delete', participant_can_delete)

rulez_registry.register("can_edit", DiscussionComment.participants.through)
rulez_registry.register("can_delete", DiscussionComment.participants.through)
