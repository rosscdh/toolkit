# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.review.models import ReviewDocument
from .user import SimpleUserWithReviewUrlSerializer
from .item import ItemSerializer


class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the ReviewDocument
    """
    reviewer = serializers.SerializerMethodField('get_reviewer')
    item = serializers.SerializerMethodField('get_item')

    class Meta:
        model = ReviewDocument
        fields = ('url', 'document', 'item', 'reviewer', 'is_complete', 'date_last_viewed')

    def get_item(self, obj):
        return ItemSerializer(obj.document.item, context=self.context).data.get('url')

    def get_reviewer(self, obj):
        reviewer = obj.reviewer
        if reviewer is not None:
            return SimpleUserWithReviewUrlSerializer(reviewer, context=self.context).data
        return None