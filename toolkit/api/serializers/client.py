# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.core.client.models import Client


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    lawyer = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', lookup_field='username')
    class Meta:
        model = Client
