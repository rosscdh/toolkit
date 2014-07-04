# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.task.models import Task
from .user import LiteUserSerializer


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    """
    """
    created_by = LiteUserSerializer(required=True, many=False)
    assigned_to = LiteUserSerializer(required=False, many=True)

    class Meta:
        model = Task
