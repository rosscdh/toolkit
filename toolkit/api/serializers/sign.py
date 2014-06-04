# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.sign.models import SignDocument
from .user import SimpleUserSerializer


class SignatureSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the SignDocument
    """
    claim_url = serializers.SerializerMethodField('get_claim_url')
    is_claimed = serializers.SerializerMethodField('get_is_claimed')
    requested_by = SimpleUserSerializer(source='requested_by', many=False)
    signers = serializers.SerializerMethodField('get_signers')
    percentage_complete = serializers.Field(source='percentage_complete')

    class Meta:
        model = SignDocument
        fields = ('url',
                  'claim_url',
                  'is_claimed',
                  'requested_by',
                  'signers',
                  'percentage_complete')

    def get_claim_url(self, obj):
        if obj.signing_request.data.get('is_claimed', False) is False:
            return obj.get_claim_url()
        return None

    def get_is_claimed(self, obj):
        signing_request = obj.signing_request
        if signing_request:
            return obj.signing_request.data.get('is_claimed', False)
        return False

    def get_signers(self, obj):
        signers = []
        for signer in obj.document.signers.all():
            singer_data = SimpleUserSerializer(signer).data
            has_signed = obj.has_signed(signer=signer)
            signed_at = obj.signed_at(signer=signer)
            singer_data.update({
                'sign_url': obj.get_absolute_url(signer=signer) if has_signed is False else None,
                'has_signed': has_signed,
                'signed_at': signed_at,
            })

            signers.append(singer_data)
        return signers
