# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.review.models import ReviewDocument
from .user import SimpleUserWithReviewUrlSerializer


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
        from .item import LiteItemSerializer
        return LiteItemSerializer(obj.document.item, context=self.context).data.get('url')

    def get_reviewer(self, obj):
        reviewer = obj.reviewer

        if reviewer is not None:
            context = self.context.copy()

            context.update({
                'review_document': obj
            })
            return SimpleUserWithReviewUrlSerializer(reviewer, context=context).data
        return None