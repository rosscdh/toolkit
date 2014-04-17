# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.sign.models import SignDocument
from .user import SimpleUserWithReviewUrlSerializer
from .item import LiteItemSerializer


class SignatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the SignDocument
    """
    signer = serializers.SerializerMethodField('get_signer')
    item = serializers.SerializerMethodField('get_item')

    class Meta:
        model = SignDocument
        fields = ('url', 'document', 'item', 'signer', 'is_complete', 'date_last_viewed')

    def get_item(self, obj):
        return LiteItemSerializer(obj.document.item, context=self.context).data.get('url')

    def get_signer(self, obj):
        signer = obj.signer
        if signer is not None:
            context = self.context.copy()
            context.update({
                'review_document': obj
            })
            return SimpleUserWithReviewUrlSerializer(signer, context=context).data
        return None