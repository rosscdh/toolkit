# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from rest_framework import serializers

from toolkit.core.item.models import Item


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.SerializerMethodField('get_status')
    latest_revision = serializers.Field(source='latest_revision')

    matter = serializers.HyperlinkedRelatedField(many=False, required=True, view_name='workspace-detail', lookup_field='slug')

    parent = serializers.HyperlinkedRelatedField(required=False, many=False, view_name='item-detail', lookup_field='slug')
    children = serializers.SerializerMethodField('get_children')

    class Meta:
        model = Item
        lookup_field = 'slug'
        fields = ('slug', 'url', 'status', 'name', 'description', 'matter',
                  'parent', 'children', 'closing_group', 'latest_revision',
                  'is_final', 'is_complete', 'date_due',
                  'date_created', 'date_modified',)

        exclude = ('data', 'responsible_party')

    def get_status(self, obj):
        """
        placeholder
        open = new and pending
        final = ready for review+signing (may not actually happen tho)
        executed = approved and signed
        'one of open|awaiting document|final|executed'
        """
        return obj.display_status

    def get_participants(self, obj):
        """
        placeholder
        '/api/v1/users/:pk'
        @TODO is this necessary for items?
        """
        return []

    def get_reviewers(self, obj):
        """
        placeholder
        """
        if obj.latest_revision is not None:
            return obj.latest_revision.reviewers.all()
        return []

    def get_signatories(self, obj):
        """
        placeholder
        """
        if obj.latest_revision is not None:
            return obj.latest_revision.signatories.all()
        return []

    def get_children(self, obj):
        return [ItemSerializer(i).data for i in obj.item_set.all()]
