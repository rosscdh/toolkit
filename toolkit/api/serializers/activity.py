# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from actstream.models import Action
from rest_framework import serializers
from toolkit.api.serializers.user import LiteUserSerializer

from .user import SimpleUserSerializer


class MatterActivitySerializer(serializers.HyperlinkedModelSerializer):
    #actor = SimpleUserSerializer('actor')
    event = serializers.SerializerMethodField('get_event')
    timesince = serializers.SerializerMethodField('get_timesince')
    actor = LiteUserSerializer('actor')

    class Meta:
        model = Action
        lookup_field = 'id'
        fields = ('id', 'actor', 'event', 'data', 'timestamp', 'timesince')

    def get_timesince(self, obj):
        return obj.timesince()

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
                return _('%(actor)s %(verb)s %(action_object)s') % ctx
            #return _('%(actor)s %(verb)s %(target)s') % ctx
        #if obj.action_object:
        #    return _('%(actor)s %(verb)s %(action_object)s') % ctx
        #return _('%(actor)s %(verb)s') % ctx
        return None


class ItemActivitySerializer(MatterActivitySerializer):
    def get_event(self, obj):
        """
        Item Actions should show a bit more info about the event
        """
        ctx = {
            'actor': obj.actor,
            'actor_pk': obj.actor.pk,
            'verb': obj.verb,
            'action_object': obj.action_object,
            'action_object_pk': obj.action_object.slug,
            'action_object_url': obj.action_object.get_absolute_url(),
            #'target': obj.target,
            #'target_pk': obj.target.slug,
        }

        return _('<span data-uid="%(actor_pk)d">%(actor)s</span> %(verb)s <a href="%(action_object_url)s">%(action_object)s</a>') % ctx
