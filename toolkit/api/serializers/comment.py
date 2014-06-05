# -*- coding: utf-8 -*-
from rest_framework import serializers
from threadedcomments.models import ThreadedComment

from .user import SimpleUserSerializer


class MatterCommentSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.SerializerMethodField('get_title')
    thread = serializers.SerializerMethodField('get_thread')
    date_created = serializers.DateTimeField(source='submit_date', read_only=True)
    last_updated = serializers.SerializerMethodField('get_last_updated')
    user = SimpleUserSerializer(required=False)

    class Meta:
        model = ThreadedComment
        fields = ('id',
                  'title',
                  'comment',
                  'date_created',
                  'last_updated',
                  'thread',
                  'user')
        lookup_field = 'id'

    def get_title(self, obj):
        return obj.title if obj.title.strip() not in [None, ''] else None

    def get_thread(self, obj):
        return MatterCommentSerializer(obj.children.all(), context=self.context, many=True).data

    def get_last_updated(self, obj):
        """
        If we are looking at the head of the thread, then get the last childs submit_date
        and make it the last modified @TODO cache this info
        """
        if obj.parent is None:
            last_item = obj.last_child
            return last_item.submit_date
        return None