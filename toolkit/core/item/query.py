# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models.query import QuerySet


class ItemQuerySet(QuerySet):
    @property
    def __task_class__(self):
        from toolkit.apps.task.models import Task
        return Task

    def mine(self, user, **kwargs):
        return self.filter(responsible_party=user, **kwargs)

    def needs_review(self, user):
        return self.filter(revision__is_current=True, revision__reviewers__in=[user])

    def needs_signature(self, user):
        return self.filter(revision__is_current=True, revision__signers__in=[user])

    def needs_upload(self, user):
        return self.filter(responsible_party=user, is_requested=True)

    def needs_tasks(self, user):
        return self.__task_class__.objects.filter(item=self, is_complete=False, assigned_to__in=[user])

    def requested(self, **kwargs):
        return self.filter(is_requested=True, **kwargs)
