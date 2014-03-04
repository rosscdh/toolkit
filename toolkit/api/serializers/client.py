# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.core.client.models import Client


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    """
    The full representation of a Client.
    """
    lawyer = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', lookup_field='username')

    class Meta:
        model = Client


class LiteClientSerializer(ClientSerializer):
    """
    The lite representation of a Client.

    Used when a client is referenced in other API objects.
    """
    class Meta(ClientSerializer.Meta):
        fields = ('name', 'url')
