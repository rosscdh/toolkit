# -*- coding: utf-8 -*-
from rest_framework import serializers
from threadedcomments.models import ThreadedComment

from .user import LiteUserSerializer


class MatterCommentSerializer(serializers.HyperlinkedModelSerializer):
    date_posted = serializers.DateTimeField(source='submit_date', read_only=True)
    user = LiteUserSerializer(required=False)

    class Meta:
        fields = ('id', 'comment', 'date_posted', 'user')
        lookup_field = 'id'
        model = ThreadedComment
