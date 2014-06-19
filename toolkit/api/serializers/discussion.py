# -*- coding: utf-8 -*-
from rest_framework import serializers

from toolkit.apps.discussion.models import DiscussionComment

from .user import SimpleUserSerializer


class DiscussionSerializer(serializers.HyperlinkedModelSerializer):
    author = SimpleUserSerializer(read_only=True, source='user')
    comments = serializers.SerializerMethodField('get_comments')
    content = serializers.WritableField(source='comment')
    date_created = serializers.DateTimeField(source='submit_date', read_only=True)
    date_updated = serializers.SerializerMethodField('get_last_updated')
    participants = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id',
                  'title',
                  'content',
                  'is_archived',
                  'comments',
                  'author',
                  'participants',
                  'date_created',
                  'date_updated',)
        lookup_field = 'id'
        model = DiscussionComment

    def get_comments(self, obj):
        return DiscussionCommentSerializer(obj.children.all(), context=self.context, many=True).data

    def get_last_updated(self, obj):
        if obj.children.count() > 0:
            return obj.last_child.submit_date
        else:
            return obj.submit_date


class LiteDiscussionSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ('id',
                  'title',
                  'content',
                  'is_archived',
                  'author',
                  'participants',
                  'date_created',
                  'date_updated',)


class DiscussionCommentSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ('id',
                  'content',
                  'author',
                  'date_created',)
