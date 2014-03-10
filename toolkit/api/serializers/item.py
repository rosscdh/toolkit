# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from rest_framework import serializers

from toolkit.core.item.models import Item
from .revision import RevisionSerializer


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    description = serializers.CharField(source='description', required=False)

    status = serializers.ChoiceField(required=False, choices=Item.ITEM_STATUS.get_choices())

    # must be read_only=True
    latest_revision = RevisionSerializer(source='latest_revision', read_only=True)

    matter = serializers.HyperlinkedRelatedField(many=False, required=True, view_name='workspace-detail', lookup_field='slug')

    parent = serializers.HyperlinkedRelatedField(required=False, many=False, view_name='item-detail', lookup_field='slug')
    children = serializers.SerializerMethodField('get_children')

    class Meta:
        model = Item
        lookup_field = 'slug'
        fields = ('slug', 'url',
                  'status',
                  'name', 'description', 'matter',
                  'parent', 'children', 'closing_group', 'category',
                  'latest_revision',
                  'is_final', 'is_complete', 'date_due',
                  'date_created', 'date_modified',)

        exclude = ('data', 'responsible_party')

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
