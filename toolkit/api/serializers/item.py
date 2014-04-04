# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from rest_framework import serializers

from toolkit.core.item.models import Item

from .revision import RevisionSerializer
from .user import LiteUserSerializer, SimpleUserWithReviewUrlSerializer


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    description = serializers.CharField(source='description', required=False)

    status = serializers.ChoiceField(required=False, choices=Item.ITEM_STATUS.get_choices())

    responsible_party = LiteUserSerializer(required=False)

    latest_revision = serializers.SerializerMethodField('get_latest_revision')

    matter = serializers.HyperlinkedRelatedField(many=False, required=True, view_name='workspace-detail', lookup_field='slug')

    parent = serializers.HyperlinkedRelatedField(required=False, many=False, view_name='item-detail', lookup_field='slug')
    children = serializers.SerializerMethodField('get_children')

    request_document_meta = serializers.SerializerMethodField('get_request_document_meta')

    class Meta:
        model = Item
        lookup_field = 'slug'
        fields = ('slug', 'url',
                  'status', 'responsible_party',
                  'name', 'description', 'matter',
                  'parent', 'children', 'closing_group', 'category',
                  'latest_revision',
                  'is_final', 'is_complete', 'is_requested',
                  'date_due', 'date_created', 'date_modified',
                  'request_document_meta',)

        exclude = ('data',)

    def get_participants(self, obj):
        """
        placeholder
        '/api/v1/users/:pk'
        @TODO is this necessary for items?
        """
        return []

    def get_latest_revision(self, obj):
        return RevisionSerializer(obj.latest_revision, context={'request': self.context.get('request')}).data

    def get_reviewers(self, obj):
        """
        placeholder
        """
        if obj.latest_revision is not None:
            return [SimpleUserWithReviewUrlSerializer(u, context=self.context).data for u in obj.latest_revision.reviewers.all()]
        return []

    def get_signers(self, obj):
        """
        placeholder
        """
        if obj.latest_revision is not None:
            return [SimpleUserWithReviewUrlSerializer(u, context=self.context).data for u in obj.latest_revision.signers.all()]
        return []

    def get_children(self, obj):
        return [ItemSerializer(i, context=self.context).data for i in obj.item_set.all()]

    def get_request_document_meta(self, obj):
        """
        Return the requested by info if present otherwise null
        see item_request.py
        """
        return obj.data.get('request_document', {
                'message': None,
                'requested_by': None,
                'date_requested': None
            })


class LiteItemSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        fields = ('url', 'slug', 'name',)
