# -*- coding: utf-8 -*-
from actstream.models import Action
from rest_framework import serializers


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    event = serializers.SerializerMethodField('get_event')

    class Meta:
        model = Action
        lookup_field = 'id'
        fields = ('id', 'event', 'data',)

    def get_event(self, obj):
        # just show a unicode-representation on GUI
        return unicode(obj)