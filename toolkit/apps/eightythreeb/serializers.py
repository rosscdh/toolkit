# -*- coding: UTF-8 -*-
from rest_framework import serializers

from .models import EightyThreeB


class EightyThreeBSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False)

    class Meta:
        model = EightyThreeB
        exclude = ('data',)
