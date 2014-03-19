# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

from actstream.models import Action
from rest_framework import serializers
from toolkit.api.serializers.user import LiteUserSerializer


class ActorObjectRelatedField(serializers.RelatedField):
    def to_native(self, value):
        return LiteUserSerializer(value).data


class MatterActivitySerializer(serializers.HyperlinkedModelSerializer):
    event = serializers.SerializerMethodField('get_event')
    timesince = serializers.SerializerMethodField('get_timesince')
    actor = ActorObjectRelatedField()

    class Meta:
        model = Action
        lookup_field = 'id'
        fields = ('id', 'actor', 'event', 'data', 'timestamp', 'timesince')

    def get_timesince(self, obj):
        return obj.timesince()

    def get_actor(self, obj):
        pass

    def get_event(self, obj):
        """
        Matter level actions should show minimalinformation about an event
        """
        ctx = {
            'actor': obj.actor,
            'verb': obj.verb,
            'action_object': obj.action_object,
            'target': obj.target,
        }
        if obj.target:
            if obj.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s') % ctx
            return _('%(actor)s %(verb)s %(target)s') % ctx
        if obj.action_object:
            return _('%(actor)s %(verb)s %(action_object)s') % ctx
        return _('%(actor)s %(verb)s') % ctx


class ItemActivitySerializer(MatterActivitySerializer):
    def get_event(self, obj):
        """
        Item Actions should show a bit more info about the event
        """
        ctx = {
            'actor': obj.actor,
            'verb': obj.verb,
            'action_object': obj.action_object,
            'target': obj.target,
        }
        if obj.target:
            if obj.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s') % ctx
            return _('%(actor)s %(verb)s %(target)s') % ctx
        if obj.action_object:
            return _('%(actor)s %(verb)s %(action_object)s') % ctx
        return _('%(actor)s %(verb)s') % ctx