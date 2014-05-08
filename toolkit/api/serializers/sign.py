# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.sign.models import SignDocument
from .user import SimpleUserWithSignUrlSerializer


class SignatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the SignDocument
    """
    signers = serializers.SerializerMethodField('get_signers')
    item = serializers.SerializerMethodField('get_item')

    class Meta:
        model = SignDocument
        fields = ('url', 'document', 'item', 'signers', 'is_complete', 'date_last_viewed')

    def get_item(self, obj):
        from .item import LiteItemSerializer
        return LiteItemSerializer(obj.document.item, context=self.context).data.get('url')

    def get_signers(self, obj):
        signers = []
        for signer in obj.document.signers.all():
            context = self.context.copy()
            context.update({
                'sign_document': obj
            })
            signers.append(SimpleUserWithSignUrlSerializer(signer, context=context).data)
        return None