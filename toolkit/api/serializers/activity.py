# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from actstream.models import Action
from rest_framework import serializers
from toolkit.api.serializers.user import LiteUserSerializer

from .user import SimpleUserSerializer


class MatterActivitySerializer(serializers.HyperlinkedModelSerializer):
    event = serializers.SerializerMethodField('get_event')
    #timesince = serializers.SerializerMethodField('get_timesince')
    #actor = LiteUserSerializer('actor')

    class Meta:
        model = Action
        lookup_field = 'id'
        fields = ('id', 'event')

    def get_timesince(self, obj):
        return obj.timesince()

    def get_event(self, obj):
        """
        Matter level actions should show minimalinformation about an event
        """
        ctx = {
            'actor': obj.actor,
            'actor_pk': obj.actor.pk,
            'verb': obj.verb,
            'action_object': obj.action_object,
            'action_object_pk': obj.action_object.slug,
            'action_object_url': obj.action_object.get_absolute_url(),
            'timestamp': obj.timestamp
            #'target': obj.target,
            #'target_pk': obj.target.slug,
        }

        if obj.__class__.__name__ in ['Item']:
            return _('<span data-uid="%(actor_pk)d">%(actor)s</span> %(verb)s <a href="%(action_object_url)s">%(action_object)s</a> <span data-date="%(timestamp)s"></span>') % ctx

        return _('<span data-uid="%(actor_pk)d">%(actor)s</span> %(verb)s <a href="%(action_object_url)s">%(action_object)s</a> <span data-date="%(timestamp)s"></span>') % ctx


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
            'timestamp': obj.timestamp
            #'target': obj.target,
            #'target_pk': obj.target.slug,
        }

        return _('<span data-uid="%(actor_pk)d">%(actor)s</span> %(verb)s <a href="%(action_object_url)s">%(action_object)s</a> <span data-date="%(timestamp)s"></span>') % ctx
