# -*- coding: utf-8 -*-
from rest_framework import serializers

from toolkit.apps.discussion.models import DiscussionComment

from .user import SimpleUserSerializer


class DiscussionSerializer(serializers.HyperlinkedModelSerializer):
    author = SimpleUserSerializer(read_only=True, source='user')
    comments = serializers.SerializerMethodField('get_comments')
    content = serializers.WritableField(source='comment')
    date_created = serializers.DateTimeField(source='submit_date', read_only=True)
    participants = serializers.SerializerMethodField('get_participants')

    class Meta:
        fields = ('slug',
                  'title',
                  'content',
                  'is_archived',
                  'comments',
                  'author',
                  'participants',
                  'date_created',
                  'date_updated',)
        model = DiscussionComment

    def get_comments(self, obj):
        queryset = DiscussionComment.objects.filter(parent=obj.id).order_by('submit_date')

        return DiscussionCommentSerializer(queryset, context=self.context, many=True).data

    def get_participants(self, obj):
        context = self.context
        context.update({ 'matter': obj.get_matter() })
        return SimpleUserSerializer(obj.participants.all(), context=context, many=True).data


class LiteDiscussionSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ('slug',
                  'title',
                  'content',
                  'is_archived',
                  'author',
                  'participants',
                  'date_created',
                  'date_updated',)


class DiscussionCommentSerializer(DiscussionSerializer):
    class Meta(DiscussionSerializer.Meta):
        fields = ('slug',
                  'content',
                  'author',
                  'date_created',)
