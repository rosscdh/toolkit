# -*- coding: UTF-8 -*-
"""
Matters are workspaces; and are composted of items, which may be a todo item
or a document item
"""
from rest_framework import serializers

from toolkit.apps.workspace.models import Workspace
from .item import ItemSerializer


class MatterSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    lawyer = serializers.RelatedField(many=False)
    participants = serializers.RelatedField(many=True)
    tools = serializers.RelatedField(many=True)

    items = serializers.SerializerMethodField('get_items')
    comments = serializers.SerializerMethodField('get_comments')
    activity = serializers.SerializerMethodField('get_activity')
    todo = serializers.SerializerMethodField('get_todo')

    class Meta:
        model = Workspace
        fields = ('slug', 'name', 'date_created', 'date_modified', 'is_deleted',
                  'lawyer', 'participants', 'tools', 'items', 'comments', 'activity', 'todo')

    def get_items(self, obj):
        """
        tmp method will eventually be replaced by matter.items_set.all()
        """
        return [ItemSerializer({}).data for i in xrange(0,2)]

    def get_comments(self, obj):
        """
        tmp method will eventually be replaced by getting all the latest
        comments form all items in a workspace @TODO cache this
        """
        return []

    def get_activity(self, obj):
        """
        tmp method will eventually be replaced by matter.activity.all()
        """
        return []

    def get_todo(self, obj):
        """
        tmp method will eventually be replaced by matter.todo.filter(user=request.user)
        """
        return []