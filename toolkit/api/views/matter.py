# -*- coding: UTF-8 -*-
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics

from rest_framework.response import Response
from toolkit.core.attachment.models import Revision

from toolkit.apps.workspace.models import Workspace

from .mixins import (MatterMixin,
                     _MetaJSONRendererMixin,
                     SpecificAttributeMixin,)

from rest_framework import status as http_status

from ..serializers import MatterSerializer
from ..serializers.matter import LiteMatterSerializer
from ..serializers.revision import EXT_WHITELIST
from ..serializers.attachment import ATTACHMENT_EXT_WHITELIST

from toolkit.apps.notification.template_loaders import ACTIVITY_TEMPLATES

import logging
logger = logging.getLogger('django.request')


#
# Have to re-output the variable names here
# can adapt them to the ng variable style here as desired
#
ITEM_COMMENTS_TEMPLATE = render_to_string(ACTIVITY_TEMPLATES.get('item-commented').name, {
    'actor_name': '{{ actor_name }}',
    'action_object_name': '{{ action_object_name }}',
    'timesince': '{{ timesince }}',
    'comment': '{{ comment }}',
})


class MatterEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    renderer_classes = (_MetaJSONRendererMixin, )

    def get_meta(self):
        default_status_labels = Revision.REVISION_STATUS.get_choices_dict()

        return {
                'matter': {
                    'status': None,
                    'is_demo': self.object.data.get('is_demo', False) if hasattr(self, 'object') is True else False
                },
                'item': {
                    'default_status': default_status_labels,
                    'custom_status': self.object.status_labels if hasattr(self, 'object') is True and self.object.status_labels else default_status_labels
                },
                'templates': {
                    'item.comment': ITEM_COMMENTS_TEMPLATE
                },
                'accepted_filetypes': {
                    'revision': EXT_WHITELIST,
                    'attachment': ATTACHMENT_EXT_WHITELIST,
                }
            }

    def get_serializer_class(self):
        if self.action == 'list':
            # @BUSINESSRULE show the light matter serializer
            # if we are looking at the list
            return LiteMatterSerializer
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        return user.workspace_set.mine(user=user)

    def pre_save(self, obj):
        """
        @BUSINESSRULE Enforce the lawyer being set as the current user
        """
        if obj.lawyer in [None, '']:
            if self.request.user.profile.is_lawyer:
                obj.lawyer = self.request.user

        return super(MatterEndpoint, self).pre_save(obj=obj)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", MatterEndpoint)
rulez_registry.register("can_edit", MatterEndpoint)
rulez_registry.register("can_delete", MatterEndpoint)


"""
Custom Api Endpoints
"""


class MatterExportView(generics.CreateAPIView, MatterMixin):
    @property
    def provider_name(self):
        if self.provider == 'box':
            return 'box.com'

        if self.provider == 'dropbox-oauth2':
            return 'dropbox.com'

        return 'a Zip file'

    def create(self, request, *args, **kwargs):
        self.provider = kwargs.get('provider', None)

        if self.provider is None:
            detail = 'Your export is being generated. Once complete, you will recieve an email with the next steps.'
        else:
            detail = 'Your matter is being exported to %s. Please check your %s account for the folder named "%s".' % (self.provider_name, self.provider_name, slugify(self.matter.name))

        try:
            self.matter.export_matter(requested_by=request.user, provider=self.provider)

            return Response(status=http_status.HTTP_200_OK, data={
                'detail': detail})

        except Exception as e:
            logger.critical('Export Error: %s for user: %s' % (e, request.user))
            return Response(status=http_status.HTTP_500_INTERNAL_SERVER_ERROR, data={
                'detail': 'An exception has occurred, our development team have been notified. We apologise for the inconvenience.'})

    def can_edit(self, user):
        """
        Only the matter.lawyer can access this functionality
        """
        return user.profile.is_lawyer is True and user in self.matter.participants.all()

rulez_registry.register("can_edit", MatterExportView)


class ClosingGroupView(SpecificAttributeMixin,
                       generics.DestroyAPIView,
                       generics.CreateAPIView,
                       generics.RetrieveAPIView,
                       MatterMixin,):
    """
    /matters/:matter_slug/closing_group/:group (GET,POST,DELETE)
        [lawyer] can assign an item to a closing group

    view/create/delete a specific closing_group
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    specific_attribute = 'closing_groups'

    def retrieve(self, request, **kwargs):
        obj = self.get_object()
        return Response(obj)

    def create(self, request, **kwargs):
        self.get_object()
        closing_group = self.kwargs.get('closing_group')

        closing_groups = self.object.add_closing_group(closing_group)
        self.object.save(update_fields=['data'])

        return Response(closing_groups)

    def delete(self, request, **kwargs):
        closing_groups = self.get_object()
        closing_group = self.kwargs.get('closing_group')

        try:
            closing_groups = self.object.remove_closing_group(closing_group, instance=self.object)
            self.object.save(update_fields=['data'])
        except Exception as e:
            logger.info('Could not delete closing_group: %s due to: %s' % (closing_group, e,))

        return Response(closing_groups)


class RevisionLabelView(generics.DestroyAPIView,
                        generics.CreateAPIView,
                        MatterMixin,):
    """
    /matters/:matter_slug/revision_label (POST)
        [lawyer] can assign an item to a closing group
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    specific_attribute = 'status_labels'

    def create(self, request, **kwargs):
        obj = self.get_object()
        status_labels = request.DATA.get('status_labels')

        obj.status_labels = status_labels
        obj.save(update_fields=['data'])
        return Response(status=http_status.HTTP_201_CREATED)

    def can_edit(self, user):
        return user.profile.is_lawyer

rulez_registry.register("can_edit", RevisionLabelView)
