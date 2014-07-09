# -*- coding: utf-8 -*-
from django.db import models

from .mixins import SendReminderEmailMixin
from .managers import TaskManager

from rulez import registry as rulez_registry

from jsonfield import JSONField
from uuidfield import UUIDField


class Task(SendReminderEmailMixin,
           models.Model):
    """
    Tasks that can be assigned to users
    """
    slug = UUIDField(auto=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255)

    item = models.ForeignKey('item.Item')

    created_by = models.ForeignKey('auth.User', related_name='created_by_user')

    is_complete = models.BooleanField(default=False)

    # blank=True as we will create it before knowing who its assigned to
    assigned_to = models.ManyToManyField('auth.User', blank=True)
    date_due = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, db_index=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    data = JSONField(default={}, blank=True)

    objects = TaskManager()

    def get_absolute_url(self):
        return self.item.get_absolute_url()

    def can_read(self, user):
        return user in self.item.matter.participants.all()

    def can_edit(self, user):
        return self.pk is None  \
               or user == self.created_by  \
               or user.matter_permissions(matter=self.item.matter).has_permission(manage_items=True) is True

    def can_delete(self, user):
        return user == self.created_by  \
               or user.matter_permissions(matter=self.item.matter).has_permission(manage_items=True) is True


rulez_registry.register("can_read", Task)
rulez_registry.register("can_edit", Task)
rulez_registry.register("can_delete", Task)