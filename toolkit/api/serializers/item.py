# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from rest_framework.reverse import reverse
from rest_framework import serializers

from toolkit.core.item.models import Item

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from .revision import SimpleRevisionSerializer
from .user import LiteUserSerializer, SimpleUserWithReviewUrlSerializer


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    description = serializers.CharField(source='description', required=False)

    regular_url = serializers.Field(source='get_regular_url')

    status = serializers.ChoiceField(required=False, choices=Item.ITEM_STATUS.get_choices())

    review_percentage_complete = serializers.Field(source='review_percentage_complete')
    signing_percentage_complete = serializers.Field(source='signing_percentage_complete')

    responsible_party = LiteUserSerializer(required=False)

    latest_revision = SimpleRevisionSerializer(read_only=True)

    matter = serializers.HyperlinkedRelatedField(many=False, required=True, view_name='workspace-detail',
                                                 lookup_field='slug')
    attachments = serializers.HyperlinkedRelatedField(many=True, view_name='attachment-detail')

    parent = serializers.HyperlinkedRelatedField(required=False, many=False, view_name='item-detail',
                                                 lookup_field='slug')
    children = serializers.SerializerMethodField('get_children')

    task_status = serializers.SerializerMethodField('get_task_status')
    last_comment_by = serializers.SerializerMethodField('get_last_comment_by')

    request_document_meta = serializers.SerializerMethodField('get_request_document_meta')

    class Meta:
        model = Item
        lookup_field = 'slug'
        fields = ('slug',
                  'url', 'regular_url',
                  'status',
                  'responsible_party',
                  'review_percentage_complete',
                  'signing_percentage_complete',
                  'name', 'description', 'matter',
                  'parent', 'children', 'closing_group', 'category',
                  'latest_revision',
                  'is_final', 'is_complete', 'is_requested',
                  'date_due', 'date_created', 'date_modified',
                  'task_status',
                  'last_comment_by',
                  'request_document_meta', 'attachments')

        exclude = ('data',)

    def get_participants(self, obj):
        """
        placeholder
        '/api/v1/users/:pk'
        @TODO is this necessary for items?
        """
        return []

    def get_latest_revision(self, obj):
        if obj.latest_revision is not None:
            return ABSOLUTE_BASE_URL(reverse('matter_item_revision', kwargs={'matter_slug': obj.matter.slug,
                                                                             'item_slug': obj.slug}))
        return None

    def get_reviewers(self, obj):
        """
        placeholder
        """
        if getattr(obj.latest_revision, 'pk', None) is not None:
            return [SimpleUserWithReviewUrlSerializer(u, context=self.context).data
                    for u in obj.latest_revision.reviewers.all()]

        return []

    def get_signers(self, obj):
        """
        placeholder
        """
        if getattr(obj.latest_revision, 'pk', None) is not None:
            return [SimpleUserWithReviewUrlSerializer(u, context=self.context).data
                    for u in obj.latest_revision.signers.all()]
        return []

    def get_children(self, obj):
        return [ItemSerializer(i, context=self.context).data for i in obj.item_set.all()]

    def get_task_status(self, obj):
        return obj.task_status

    def get_last_comment_by(self, obj):
      request = self.context.get('request', None)
      user = getattr(request, 'user', None)

      if user is None:
        return None

      role = user.matter_permissions(matter=obj.matter).role_name

      if role in ['owner', 'colleague']:
        # show colleague comments otherwise public
        return obj.last_comment_by(is_public=False)
      else:
        # show public comments otherwise none
        return obj.last_comment_by(is_public=True)


    def get_request_document_meta(self, obj):
        """
        Return the requested by info if present otherwise null
        see revision_request.py
        """
        return obj.data.get('request_document', {
                'message': None,
                'requested_by': None,
                'date_requested': None
            })


class SimpleItemSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        fields = ('url', 'slug',
                  'name', 'description',
                  'status',
                  'review_percentage_complete',
                  'signing_percentage_complete',
                  'category',
                  'latest_revision',
                  'is_final', 'is_complete', 'is_requested',
                  'task_status',
                  'last_comment_by',
                  'date_due',)


class LiteItemSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        fields = ('url', 'slug', 'name',)
