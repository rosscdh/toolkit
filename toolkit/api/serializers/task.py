# -*- coding: UTF-8 -*-
from rest_framework import serializers

from toolkit.apps.task.models import Task
from .user import SimpleUserSerializer


class CreateTaskSerializer(serializers.HyperlinkedModelSerializer):
    """
    When creating tasks we need to pass in a set of usernames for created_by and assigned_to
    """
    created_by = serializers.SlugRelatedField(required=True, many=False, slug_field='username')
    assigned_to = serializers.SlugRelatedField(required=False, many=True, slug_field='username')

    class Meta:
        model = Task
        exclude = ('data',)


class TaskSerializer(CreateTaskSerializer):
    """
    For GET of tasks we use the SimpleUserSerializer objects
    """
    created_by = SimpleUserSerializer(source='created_by', many=False)
    assigned_to = SimpleUserSerializer(source='assigned_to', many=True, required=False, allow_add_remove=True, read_only=False)

    class Meta:
        model = Task
        exclude = ('data',)