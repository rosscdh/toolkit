# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save

from toolkit.core.mixins import IsDeletedMixin
from toolkit.core.signals import on_workspace_post_save

from toolkit.utils import _class_importer

from rulez import registry as rulez_registry

from uuidfield import UUIDField
from jsonfield import JSONField

from .managers import WorkspaceManager
from .mixins import ClosingGroupsMixin, CategoriesMixin


class Workspace(IsDeletedMixin, ClosingGroupsMixin, CategoriesMixin, models.Model):
    """
    Workspaces are areas that allow multiple tools
    to be associated with a group of users
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)

    slug = models.SlugField(blank=True)
    matter_code = models.SlugField(null=True, blank=True)

    lawyer = models.ForeignKey('auth.User', null=True, related_name='lawyer_workspace')  # Lawyer that created this workspace
    client = models.ForeignKey('client.Client', null=True, blank=True)

    participants = models.ManyToManyField('auth.User', blank=True)

    tools = models.ManyToManyField('workspace.Tool', blank=True)

    data = JSONField(default={})

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ['name', '-pk']

    def __unicode__(self):
        return '%s' % self.name

    @property
    def get_lawyer(self):
        """
        if lawyer is not set then look in participants for it
        """
        lawyer = [u for u in self.participants.select_related('profile').all() if u.profile.is_lawyer is True]
        try:
            return lawyer[0]
        except IndexError:
            return None

    def get_absolute_url(self):
        """
        @BUSINESSRULE append checklist to the url
        """
        return '%s#/checklist' % reverse('matter:detail', kwargs={'matter_slug': self.slug})

    def available_tools(self):
        return Tool.objects.exclude(pk__in=[t.pk for t in self.tools.all()])

    def can_read(self, user):
        return user in self.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and (user == self.lawyer or user in self.participants.all())

    def can_delete(self, user):
        return user.profile.is_lawyer and (user == self.lawyer or user in self.participants.all())

post_save.connect(on_workspace_post_save, sender=Workspace)

rulez_registry.register("can_read", Workspace)
rulez_registry.register("can_edit", Workspace)
rulez_registry.register("can_delete", Workspace)


class InviteKey(models.Model):
    """
    Invite Key that allows a user to be invited to one or more projects
    """
    key = UUIDField(auto=True, db_index=True)
    invited_user = models.ForeignKey('auth.User', related_name='invitations')
    # is null and blank to allow us to do 1 invitekey per user
    inviting_user = models.ForeignKey('auth.User', blank=True, null=True, related_name='invitiations_made')
    matter = models.ForeignKey('workspace.Workspace', blank=True, null=True)
    tool = models.ForeignKey('workspace.Tool', blank=True, null=True)
    tool_object_id = models.IntegerField(blank=True, null=True)
    next = models.CharField(max_length=255, blank=True)  # user will be redirected here on login
    data = JSONField(default={})  # for any extra data that needs to be stored
    has_been_used = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('public:invite', kwargs={'key': self.key})

    def get_workspace_url(self):
        tool_instance = self.tool.model.objects.get(pk=self.tool_object_id)
        return tool_instance.workspace.get_absolute_url()

    def get_tool_instance_absolute_url(self):
        try:
            tool_instance = self.tool.model.objects.get(pk=self.tool_object_id)
            return tool_instance.get_absolute_url()
        except ObjectDoesNotExist:
            return None

    def get_invite_login_url(self, request=None):
        return request.build_absolute_uri(self.get_absolute_url()) if request is not None else self.get_absolute_url()


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
    def description(self):
        return self.data.get('description')

    @property
    def summary(self):
        return self.data.get('summary')

    @property
    def short_name(self):
        return self.data.get('short_name')

    @property
    def userclass_that_can_create(self):
        return self.data.get('can_create', [])

    @property
    def markers(self):
        markers = self.data.get('markers', None)
        return None if markers is None else _class_importer(markers)()

    @property
    def model(self):
        """
        return the model
        """
        app_label, model_name = (self.data.get('app_label', None), self.data.get('model_name', None),)

        if model_name is None or model_name is None:
            raise Exception('app_label and model_name need to be specified for the "%s" type' % self.__name__)

        return get_model(app_label=app_label, model_name=model_name)

    def get_form(self, user, form_key=None):
        """
        return the form class as specified in the tool object
        """
        forms = self.data.get('forms')
        form_class = forms.get(user.profile.user_class if form_key is None else form_key)  # allow us to override the form selected

        return _class_importer(form_class)

    @property
    def icon(self):
        return self.data.get('icon', 'images/icons/mail.svg')

"""
Import workspace signals
"""
from .signals import (ensure_workspace_slug,
                      ensure_workspace_matter_code,
                      ensure_workspace_has_83b_by_default,
                      ensure_tool_slug)
