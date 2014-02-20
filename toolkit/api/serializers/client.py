# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.core.client.models import Client


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
