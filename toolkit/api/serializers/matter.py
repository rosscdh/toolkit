# -*- coding: UTF-8 -*-
"""
Matters are workspaces; and are composted of items, which may be a todo item
or a document item
"""
from rest_framework import serializers
from toolkit.apps.workspace.models import Workspace

from toolkit.apps.workspace.models import (ROLES,
                                           MATTER_OWNER_PERMISSIONS)
from .client import LiteClientSerializer
from .item import SimpleItemSerializer
from .user import LiteUserSerializer

import pytz
import datetime


class ExportInfoSerializer(serializers.Serializer):
    last_exported = serializers.DateTimeField(read_only=True, required=False)
    last_export_requested = serializers.DateTimeField(read_only=True, required=False)
    download_valid_until = serializers.DateTimeField(read_only=True, required=False)

    last_exported_by = serializers.CharField(max_length=255, read_only=True, required=False)
    last_export_requested_by = serializers.CharField(max_length=255, read_only=True, required=False)

    download_url = serializers.SerializerMethodField('get_download_url')

    def get_download_url(self, obj):
        if obj.get('download_valid_until') is not None and datetime.datetime.utcnow().replace(tzinfo=pytz.utc) < obj.get('download_valid_until'):
            return obj.get('download_url')
        return None


class MatterSerializer(serializers.HyperlinkedModelSerializer):
    slug = serializers.CharField(read_only=True)

    regular_url = serializers.Field(source='get_regular_url')
    # django url # @TODO depreciate this url in facour of get_regular_url
    base_url = serializers.Field(source='get_regular_url')

    matter_code = serializers.CharField(required=False)
    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    client = LiteClientSerializer(required=False)
    lawyer = serializers.SerializerMethodField('get_lawyer')
    participants = serializers.SerializerMethodField('get_participants')

    categories = serializers.SerializerMethodField('get_categories')
    closing_groups = serializers.SerializerMethodField('get_closing_groups')

    items = serializers.SerializerMethodField('get_items')

    current_user = serializers.SerializerMethodField('get_current_user')
    roles = serializers.SerializerMethodField('get_roles')

    percent_complete = serializers.SerializerMethodField('get_percent_complete')

    export_info = serializers.SerializerMethodField('get_export_info')

    class Meta:
        model = Workspace
        fields = ('slug',
                  'url', 'regular_url',
                  'name', 'matter_code',
                  'client', 'lawyer', 'participants',
                  'closing_groups', 'categories',
                  'items',
                  'current_user', 'roles',
                  'date_created', 'date_modified',
                  'percent_complete')

    def get_closing_groups(self, obj):
        """
        placeholder
        list of closing groups
        """
        return obj.closing_groups

    def get_categories(self, obj):
        """
        placeholder
        list of categories
        """
        return obj.categories

    def get_items(self, obj):
        """
        tmp method will eventually be replaced by matter.items_set.all()
        """
        return SimpleItemSerializer(obj.item_set.filter(parent=None), context=self.context, many=True).data

    def get_lawyer(self, obj):
        owner_data = LiteUserSerializer(obj.lawyer).data
        owner_data.update({
            'role': ROLES.get_name_by_value(ROLES.owner),
            'permissions': MATTER_OWNER_PERMISSIONS,
        })
        return owner_data

    def get_participants(self, obj):
        context = self.context
        context.update({'matter': obj})
        #return LiteUserSerializer(obj.participants.all(), context=context, many=True).data
        return obj.data.get('participants', [])

    def get_current_user(self, obj):
        request = self.context.get('request')

        context = self.context
        context.update({'matter': obj})

        current_user = None

        if request:
            current_user = LiteUserSerializer(request.user, context=context).data
            profile = request.user.profile

            current_user.update({
                'counts': {
                    'requests': profile.open_requests,
                },
                'integrations': [i.get('provider') for i in request.user.social_auth.all().values('provider')],
                'firm_name': profile.firm_name,
                'has_notifications': profile.has_notifications,
                'matters_created': profile.matters_created,
            })

        return current_user

    def get_roles(self, obj):
        request = self.context.get('request')
        return {name: desc for value, name, desc in request.user.matter_permissions(matter=obj).ROLES.get_all()} if request else {}

    def get_percent_complete(self, obj):
        return obj.get_percent_complete

    def get_export_info(self, obj):
        export_info = ExportInfoSerializer(obj.export_info)
        return export_info.data


class LiteMatterSerializer(MatterSerializer):
    """
    @BUSINESSRULE used for the matters/ GET (shows lighter version of the serializer)
    """
    class Meta(MatterSerializer.Meta):
        fields = ('url', 'base_url', 'regular_url',
                  'name', 'slug', 'matter_code',
                  'client',
                  'lawyer',
                  'participants',
                  'date_created', 'date_modified',
                  'percent_complete',
                  'export_info')


class SimpleMatterSerializer(MatterSerializer):
    django_url = serializers.SerializerMethodField('get_django_url')

    class Meta(MatterSerializer.Meta):
        fields = ('django_url', 'name',)

    def get_django_url(self, obj):
        return '%s' % obj.get_absolute_url()
