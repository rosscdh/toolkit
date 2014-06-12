# -*- coding: utf-8 -*-
from rest_framework import serializers
from threadedcomments.models import ThreadedComment

from .user import SimpleUserSerializer


class DiscussionSerializer(serializers.HyperlinkedModelSerializer):
    comments = serializers.SerializerMethodField('get_comments')
    date_created = serializers.DateTimeField(source='submit_date', read_only=True)
    date_updated = serializers.SerializerMethodField('get_last_updated')
    user = SimpleUserSerializer(required=False)

    class Meta:
        fields = ('id',
                  'comment',
                  'comments',
                  'title',
                  'user',
                  'date_created',
                  'date_updated',)
        lookup_field = 'id'
        model = ThreadedComment

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
                  'comment',
                  'title',
                  'user',
                  'date_created',
                  'date_updated',)


class DiscussionCommentSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ('id',
                  'comment',
                  'user',
                  'date_created',)
