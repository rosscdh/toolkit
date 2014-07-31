# -*- coding: utf-8 -*-
from django.contrib.comments.managers import CommentManager
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from jsonfield import JSONField
from rulez import registry as rulez_registry
from threadedcomments.models import ThreadedComment
from uuidfield import UUIDField

from toolkit.apps.discussion.mailers import DiscussionAddedUserEmail, DiscussionCommentedEmail
from toolkit.apps.workspace.models import ROLES, Workspace
from toolkit.core.item.models import Item


class DiscussionComment(ThreadedComment, models.Model):
    slug = UUIDField(auto=True, db_index=True)
    participants = models.ManyToManyField('auth.User')
    is_archived = models.BooleanField(default=False)
    date_updated = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    data = JSONField(default={})

    objects = CommentManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        url = reverse('matter:detail', kwargs={ 'matter_slug': self.get_matter().slug })

        if self.is_item_discussion:
            return '{url}#/checklist/{item_slug}'.format(url=url, item_slug=self.item.slug)
        elif self.is_matter_discussion:
            return '{url}#/discussion/{thread_slug}'.format(url=url, thread_slug=self.thread.slug)

    def save(self, *args, **kwargs):
        super(DiscussionComment, self).save(*args, **kwargs)
        if self.parent_id:
            DiscussionComment.objects.filter(pk=self.parent_id).update(date_updated=self.date_updated)

    def archive(self, is_archived=True):
        self.is_archived = is_archived
        self.save(update_fields=['is_archived'])
    archive.alters_data = True

    @property
    def item(self):
        return self.content_object

    @item.setter
    def item(self, value):
        self.content_type_id = ContentType.objects.get_for_model(Item).pk
        self.object_pk = value.pk

    @property
    def matter(self):
        return self.content_object

    @matter.setter
    def matter(self, value):
        self.content_type_id = ContentType.objects.get_for_model(Workspace).pk
        self.object_pk = value.pk

    @property
    def thread(self):
        if self.parent_id:
            return DiscussionComment.objects.get(pk=self.parent_id)
        else:
            return self

    def send_added_user_email(self, actor, user, **kwargs):
        kwargs.update(self.get_email_kwargs())
        kwargs.update({'actor': actor})

        mailer = DiscussionAddedUserEmail(recipients=[(user.get_full_name(), user.email)])
        mailer.process(**kwargs)

    def send_commented_email(self, **kwargs):
        kwargs.update(self.get_email_kwargs())
        recipients = [(u.get_full_name(), u.email) for u in self.get_participants().exclude(pk=self.user.pk)]

        if recipients:
            mailer = DiscussionCommentedEmail(recipients=recipients)
            mailer.process(**kwargs)

    def get_email_kwargs(self):
        return {
            'access_url': self.get_absolute_url(),
            'actor': self.user,
            'comment': self,
            'matter': self.get_matter(),
            'object': self.get_primary_object(),
            'object_type': self.get_object_type(),
        }

    def get_participants(self):
        if self.is_item_discussion:
            return self.get_matter().participants.all() if self.is_public else self.get_matter().something.all()
        elif self.is_matter_discussion:
            return self.thread.participants.all()

    @property
    def is_item_discussion(self):
        return self.content_type_id == ContentType.objects.get_for_model(Item).pk

    @property
    def is_matter_discussion(self):
        return self.content_type_id == ContentType.objects.get_for_model(Workspace).pk

    def get_matter(self):
        if self.is_item_discussion:
            return self.item.matter
        elif self.is_matter_discussion:
            return self.matter

    def get_primary_object(self):
        if self.is_item_discussion:
            return self.item
        elif self.is_matter_discussion:
            return self.thread

    def get_object_type(self):
        if self.is_item_discussion:
            return 'item'
        elif self.is_matter_discussion:
            return 'thread'

    def can_read(self, user):
        if self.is_public:
            return True
        else:
            return user in self.get_participants()

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
    # matter owners can delete too
    return user == self.user or user in self.discussioncomment.get_matter().owners.all()

DiscussionComment.participants.through.add_to_class('can_edit', participant_can_edit)
DiscussionComment.participants.through.add_to_class('can_delete', participant_can_delete)

rulez_registry.register("can_edit", DiscussionComment.participants.through)
rulez_registry.register("can_delete", DiscussionComment.participants.through)
