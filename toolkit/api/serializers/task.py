# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.task.models import Task
# from .user import LiteUserSerializer


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    """
    """
    created_by = serializers.SlugRelatedField(required=True, many=False, slug_field='username')
    assigned_to = serializers.SlugRelatedField(required=False, many=True, slug_field='username')

    class Meta:
        model = Task
