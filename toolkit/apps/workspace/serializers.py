# -*- coding: UTF-8 -*-
from rest_framework import serializers

from .models import InviteKey, Tool


class InviteKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteKey
        exclude = ('data',)


class WorkspaceToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        exclude = ('data',)