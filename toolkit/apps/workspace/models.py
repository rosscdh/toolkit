# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model

from toolkit.utils import _class_importer

from rulez import registry as rulez_registry

from uuidfield import UUIDField
from jsonfield import JSONField



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

    def __unicode__(self):
        return '%s' % self.name

    def can_read(self, user):
        return user in self.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and user in self.participants.all()

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.participants.all()

    def get_absolute_url(self):
        return reverse('workspace:view', kwargs={'slug': self.slug})

    def available_tools(self):
        return Tool.objects.exclude(pk__in=[t.pk for t in self.tools.all()])


rulez_registry.register("can_read", Workspace)
rulez_registry.register("can_edit", Workspace)
rulez_registry.register("can_delete", Workspace)


class InviteKey(models.Model):
    """
    Invite Key that allows a user to be invited to one or more projects
    """
    key = UUIDField(auto=True, db_index=True)
    user = models.ForeignKey('auth.User')
    tool = models.ForeignKey('workspace.Tool', blank=True)
    tool_object_id = models.IntegerField(blank=True)
    next = models.CharField(max_length=255, blank=True)  # user will be redirected here on login
    data = JSONField(default={})  # for any extra data that needs to be stored
    has_been_used = models.BooleanField(default=False)


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
