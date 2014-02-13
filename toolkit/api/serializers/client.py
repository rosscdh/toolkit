# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.default.models import UserProfile


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        #exclude = ()
