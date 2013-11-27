# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from jsonfield import JSONField


class Workspace(models.Model):
    """
    Workspaces are areas that allow multiple tools
    to be associated with a group of users
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    users = models.ManyToManyField('auth.User', blank=True)
    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    def get_absolute_url(self):
        return reverse('workspace:view', kwargs={'slug': self.slug})

from .signals import ensure_workspace_slug