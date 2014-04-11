# -*- coding: utf-8 -*-
from django.template import loader

from actstream.models import Action
from rest_framework import serializers

from toolkit.api.serializers.item import LiteItemSerializer
from toolkit.api.serializers.user import LiteUserSerializer

default_template = loader.get_template('activity/default.html')  # allow override of template_name
item_comment_template = loader.get_template('activity/item_comment.html')  # allow override of template_name
revision_comment_template = loader.get_template('activity/revision_comment.html')  # allow override of template_name


def _get_activity_display(ctx, template):
    context = loader.Context(ctx)
    # render the template with passed in context
    return template.render(context)


class MatterActivitySerializer(serializers.HyperlinkedModelSerializer):
    event = serializers.SerializerMethodField('get_event')

    timesince = serializers.SerializerMethodField('get_timesince')
    actor = LiteUserSerializer('actor')
    action_object = LiteItemSerializer('action_object')
                        # TODO: change this to a generic one with URL. action_object can be Item/Revision/Matter/...
                        # instead we could use the rendered event-html in the gui

    class Meta:
        model = Action
        lookup_field = 'id'
        fields = ('id', 'actor', 'action_object', 'event', 'data', 'timestamp', 'timesince')

    def get_timesince(self, obj):
        return obj.timesince()

    def get_event(self, obj):
        """
        THIS FUNCTION SEEMS NOT TO BE USED.

        Matter level actions should show minimalinformation about an event
        """
        ctx = {
            'actor': obj.actor,
            'actor_pk': obj.actor.pk,
            'verb': obj.verb,
            'action_object': obj.action_object,
            'action_object_pk': obj.action_object.slug if obj.action_object else None,
            'action_object_url': obj.action_object.get_absolute_url() if obj.action_object and hasattr(obj.action_object, 'get_absolute_url') else None,
            'timestamp': obj.timestamp,
            'timesince': obj.timesince(),
            'data': obj.data,
            #'target': obj.target,
            #'target_pk': obj.target.slug,
        }

        # override_message = obj.data.get('override_message', None)

        # TODO: move get_verb_slug out of MatterActivityEventService
        verb_slug = obj.target.actions.get_verb_slug(obj.action_object, obj.verb)
        template = default_template

        if verb_slug == 'item-commented':
            # comment-template
            template = item_comment_template

        if verb_slug == 'revision-added-revision-comment':
            # crocodoc-template
            template = revision_comment_template
            ctx.update({'action_object_url': "%s/%s" % (obj.data['item']['latest_revision'], obj.action_object.slug)})

        return _get_activity_display(ctx, template)
        #
        # if comment is not None:
        #     return _get_comment_display(ctx, comment)
        #
        # if override_message is not None:
        #     return override_message % ctx
        #
        # if obj.action_object.__class__.__name__ in ['Item']:
        #     return _('<span data-uid="%(actor_pk)d">%(actor)s</span> %(verb)s <a href="%(action_object_url)s">%(action_object)s</a> <span data-date="%(timestamp)s"></span>') % ctx
        #
        # return _('<span data-uid="%(actor_pk)d">%(actor)s</span> %(verb)s <a href="%(action_object_url)s">%(action_object)s</a> <span data-date="%(timestamp)s"></span>') % ctx


class ItemActivitySerializer(MatterActivitySerializer):
    pass
    # def get_event(self, obj):
    #     """
    #     Item Actions should show a bit more info about the event
    #     """
    #     ctx = {
    #         'actor': obj.actor,
    #         'actor_pk': obj.actor.pk,
    #         'verb': obj.verb,
    #         'action_object': obj.action_object,
    #         'action_object_pk': obj.action_object.slug if obj.action_object else None,
    #         'action_object_url': obj.action_object.get_absolute_url() if obj.action_object and hasattr(obj.action_object, 'get_absolute_url') else None,
    #         'timestamp': obj.timestamp,
    #         'timesince': obj.timesince(),
    #         #'target': obj.target,
    #         #'target_pk': obj.target.slug,
    #     }
    #     comment = obj.data.get('comment', None)
    #
    #     if comment is not None:
    #         return _get_comment_display(ctx, comment)
    #
    #     override_message = obj.data.get('override_message', None)
    #
    #     if override_message is not None:
    #         return override_message % ctx
    #
    #     return _('<span data-uid="%(actor_pk)d">%(actor)s</span> %(verb)s <a href="%(action_object_url)s">%(action_object)s</a> <span data-date="%(timestamp)s"></span>') % ctx
