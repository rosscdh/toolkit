# -*- coding: utf-8 -*-
from actstream.models import Action
from rest_framework import serializers

__author__ = 'Marius Burfey <marius.burfey@ambient-innovation.com> - 11.03.14'


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    event = serializers.SerializerMethodField('get_event')

    class Meta:
        model = Action
        lookup_field = 'id'
        fields = ('id', 'event', 'data',)

    def get_event(self, obj):
        # just show a unicode-representation on GUI
        return unicode(obj)