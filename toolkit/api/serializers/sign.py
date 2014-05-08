# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.sign.models import SignDocument
from .user import SimpleUserSerializer


class SignatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the SignDocument
    """
    sign_url = serializers.SerializerMethodField('get_sign_url')
    claim_url = serializers.SerializerMethodField('get_claim_url')
    is_claimed = serializers.SerializerMethodField('get_is_claimed')
    signers = serializers.SerializerMethodField('get_signers')

    class Meta:
        model = SignDocument
        fields = ('url',
                  'sign_url',
                  'claim_url',
                  'signers',
                  'is_claimed',)

    def get_sign_url(self, obj):
        return obj.get_absolute_url()

    def get_claim_url(self, obj):
        return obj.get_claim_url()

    def get_is_claimed(self, obj):
        signing_request = obj.signing_request
        if signing_request:
            return obj.signing_request.data.get('is_claimed', False)
        return False

    def get_signers(self, obj):
        signers = []
        for signer in obj.document.signers.all():
            signers.append(SimpleUserSerializer(signer).data)
        return signers
