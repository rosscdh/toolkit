# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model

from jsonfield import JSONField


def _class_importer(name):
    """
    func used to import the bunch classes from string
    """
    try:
        components = name.split('.')
        module_path = components[:-1]
        klass = components[-1:]
        mod = __import__('.'.join(module_path), fromlist=klass)  # import the class and module
        klass = getattr(mod, klass[0])
    except AttributeError:
        klass = None
    return klass


class Workspace(models.Model):
    """
    Workspaces are areas that allow multiple tools
    to be associated with a group of users
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    participants = models.ManyToManyField('auth.User', blank=True)
    tools = models.ManyToManyField('workspace.Tool', blank=True)
    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['name', '-pk']

    def get_absolute_url(self):
        return reverse('workspace:view', kwargs={'slug': self.slug})

    def available_tools(self):
        return Tool.objects.exclude(pk__in=[t.pk for t in self.tools.all()])


class Tool(models.Model):
    """
    The tools we have to offer in our workspaces
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    data = JSONField(default={}, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return '%s' % self.name

    @property
    def short_name(self):
        return self.data.get('short_name')

    @property
    def model(self):
        """
        return the model
        """
        app_label, model_name = (self.data.get('app_label', None), self.data.get('model_name', None),)

        if model_name is None or model_name is None:
            raise Exception('app_label and model_name need to be specified for the "%s" type' % self.__class__.__name__)

        return get_model(app_label=app_label, model_name=model_name)

    @property
    def form(self):
        """
        return the form class as specified in the tool object
        """
        form_class = self.data.get('form')
        return _class_importer(form_class)

    @property
    def icon(self):
        return self.data.get('icon', 'images/icons/mail.svg')


"""
Import workspace signals
"""
from .signals import (ensure_workspace_slug,
                     ensure_workspace_has_83b_by_default,
                     ensure_83b_user_in_workspace_participants,
                     ensure_tool_slug)