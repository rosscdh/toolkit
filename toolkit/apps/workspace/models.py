# -*- coding: utf-8 -*-
import os
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.template.defaultfilters import slugify
from toolkit.core import _managed_S3BotoStorage

from toolkit.core.mixins import IsDeletedMixin, ApiSerializerMixin
from toolkit.apps.matter.mixins import MatterExportMixin

from dj_authy.models import AuthyModelMixin

from .signals import (ensure_workspace_slug,
                      ensure_workspace_matter_code,
                      # tool
                      ensure_tool_slug,
                      on_workspace_post_delete,
                      on_workspace_post_save)

from toolkit.utils import _class_importer

from rulez import registry as rulez_registry

from uuidfield import UUIDField
from jsonfield import JSONField

from .managers import WorkspaceManager
from .mixins import ClosingGroupsMixin, CategoriesMixin, RevisionLabelMixin


class MatterUser(models.Model):
    matter = models.ForeignKey('Workspace')
    user = models.ForeignKey('auth.User')

    data = JSONField(default={})


class Workspace(IsDeletedMixin,
                AuthyModelMixin,
                MatterExportMixin,
                ClosingGroupsMixin,
                CategoriesMixin,
                ApiSerializerMixin,
                RevisionLabelMixin,
                models.Model):
    """
    Workspaces are areas that allow multiple tools
    to be associated with a group of users
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)

    slug = models.SlugField(blank=True)
    matter_code = models.SlugField(max_length=128, null=True, blank=True)

    lawyer = models.ForeignKey('auth.User', null=True, related_name='lawyer_workspace')  # Lawyer that created this workspace
    client = models.ForeignKey('client.Client', null=True, blank=True)

    participants = models.ManyToManyField('auth.User', blank=True, through=MatterUser)

    tools = models.ManyToManyField('workspace.Tool', blank=True)

    data = JSONField(default={})

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    objects = WorkspaceManager()

    _actions = None  # private variable for MatterActivityEventService
    _serializer = 'toolkit.api.serializers.LiteMatterSerializer'

    class Meta:
        ordering = ['name', '-pk']
        verbose_name = 'Matter'
        verbose_name_plural = 'Matters'
        permissions = (
            ("manage_participants", u"Can manage participants"),
            ("manage_requests", u"Can manage requests"),
            ("manage_items", u"Can manage checklist items and categories"),
            ("manage_signatures", u"Can manage signatures & send documents for signature"),
            ("manage_clients", u"Can manage clients"),
        )

    def __init__(self, *args, **kwargs):
        #
        # Initialize the actions property
        #
        from toolkit.core.services.matter_activity import MatterActivityEventService  # cyclic
        self._actions = MatterActivityEventService(self)
        super(Workspace, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.name

    @property
    def actions(self):
        return self._actions

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

    def get_regular_url(self):
        """
        Used in notficiations & activity
        """
        return self.get_absolute_url()

    def available_tools(self):
        return Tool.objects.exclude(pk__in=[t.pk for t in self.tools.all()])

    def update_percent_complete(self):
        all_items_count = self.item_set.count()
        value = 0
        if all_items_count > 0:
            value = float(self.item_set.filter(is_complete=True).count()) / float(all_items_count)
            value = round(value * 100, 0)
        self.data['percent_complete'] = "{0:.0f}%".format(value)
        self.save(update_fields=['data'])

    def get_percent_complete(self):
        return self.data.get('percent_complete', "{0:.0f}%".format(0))

    def can_read(self, user):
        return user in self.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and (user == self.lawyer or user in self.participants.all())

    def can_delete(self, user):
        return user.profile.is_lawyer and (user == self.lawyer)

"""
Connect signals
"""
pre_save.connect(ensure_workspace_slug, sender=Workspace, dispatch_uid='workspace.pre_save.ensure_workspace_slug')
pre_save.connect(ensure_workspace_matter_code, sender=Workspace, dispatch_uid='workspace.pre_save.ensure_workspace_matter_code')

post_delete.connect(on_workspace_post_delete, sender=Workspace, dispatch_uid='workspace.post_delete.on_workspace_post_delete')
post_save.connect(on_workspace_post_save, sender=Workspace, dispatch_uid='workspace.post_save.on_workspace_post_save')


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
        except:
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
Connect Signals
"""
pre_save.connect(ensure_tool_slug, sender=Tool, dispatch_uid='workspace.ensure_tool_slug')
