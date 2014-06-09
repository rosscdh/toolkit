# -*- coding: utf-8 -*-
from rest_framework import serializers
from threadedcomments.models import ThreadedComment

from .user import SimpleUserSerializer


class DiscussionSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.SerializerMethodField('get_title')
    comments = serializers.SerializerMethodField('get_comments')
    excerpt = serializers.Field(source='comment')
    date_created = serializers.DateTimeField(source='submit_date', read_only=True)
    date_updated = serializers.SerializerMethodField('get_last_updated')
    user = SimpleUserSerializer(required=False)

    class Meta:
        fields = ('id',
                  'title',
                  'excerpt',
                  'user',
                  'comments',
                  'date_created',
                  'date_updated',)
        lookup_field = 'id'
        model = ThreadedComment

    def get_title(self, obj):
        return obj.title if obj.title.strip() not in [None, ''] else None

    def get_comments(self, obj):
        return DiscussionCommentSerializer(obj.children.all(), context=self.context, many=True).data

    def get_last_updated(self, obj):
        # if obj.parent is None:
            # last_item = obj.last_child
            # return last_item.submit_date
        return obj.submit_date


class LiteDiscussionSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ('id',
                  'title',
                  'excerpt',
                  'user',
                  'date_created',
                  'date_updated',)


class DiscussionCommentSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ('id',
                  'comment',
                  'user',
                  'date_created',)
