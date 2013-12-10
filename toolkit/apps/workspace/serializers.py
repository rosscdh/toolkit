# -*- coding: UTF-8 -*-
from rest_framework import serializers

from .models import InviteKey


class InviteKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteKey
        exclude = ('data',)
