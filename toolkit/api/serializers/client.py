# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        #exclude = ()
