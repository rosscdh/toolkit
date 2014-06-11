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
        if obj is not None and obj.signing_request is not None:
                return obj.get_claim_url() if obj.signing_request.data.get('is_claimed', False) is False else None
        return None

    def get_is_claimed(self, obj):
        if obj is not None:
            signing_request = obj.signing_request
            if signing_request:
                return obj.signing_request.data.get('is_claimed', False)
        return False

    def get_signers(self, obj):
        signers = []
        if obj is not None:
            for signer in obj.document.signers.all():

                singer_data = SimpleUserSerializer(signer).data
                #
                # Can only have a signing url and that data after the doc has been claimed
                #
                if obj.signing_request.data.get('is_claimed', False) is True:

                    has_signed = obj.has_signed(signer=signer)
                    signed_at = obj.signed_at(signer=signer)

                    # dotn show the sign_url if the user has_signed already
                    singer_data.update({
                        'sign_url': obj.get_absolute_url(signer=signer) if has_signed is False else None,
                        'has_signed': has_signed,
                        'signed_at': signed_at,
                    })

                signers.append(singer_data)
        return signers
