# -*- coding: utf-8 -*-
from django.template import loader

from actstream.models import Action
from rest_framework import serializers

from toolkit.api.serializers.item import LiteItemSerializer
from toolkit.api.serializers.user import LiteUserSerializer
from toolkit.core.item.models import Item

from toolkit.core.services.matter_activity import get_verb_slug


ACTIVITY_TEMPLATES = {
    'default': loader.get_template('activity/default.html'),
    'item-commented': loader.get_template('activity/item_comment.html'),
    'revision-added-review-session-comment': loader.get_template('activity/review_session_comment.html'),
    'revision-added-revision-comment': loader.get_template('activity/revision_comment.html'),
}


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

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs and 'request' in kwargs['context']:
            self.request = kwargs['context']['request']
        super(MatterActivitySerializer, self).__init__(*args, **kwargs)

    def get_event(self, obj):
        """
        Matter level actions should show minimalinformation about an event
        """
        message = obj.data.get('override_message', None)
        if message is None:
            message = "%s %s %s" % (obj.actor, obj.verb, obj.action_object)

        ctx = {
            'actor': obj.actor,
            'actor_pk': obj.actor.pk,
            # 'verb': obj.verb,
            'action_object': obj.action_object,
            'action_object_url': obj.action_object.get_absolute_url() if obj.action_object and hasattr(obj.action_object, 'get_absolute_url') else None,
            'timestamp': obj.timestamp,
            'timesince': obj.timesince(),
            'message': message,
            'comment': obj.data.get('comment', None),
            # 'data': obj.data,
            #'target': obj.target,
            #'target_pk': obj.target.slug,
        }

        verb_slug = get_verb_slug(obj.action_object, obj.verb)
        template = ACTIVITY_TEMPLATES.get(verb_slug, ACTIVITY_TEMPLATES.get('default'))

        if verb_slug in ['revision-added-review-session-comment', 'revision-added-revision-comment']:
            # exception for revision-commens:
            # add item, revision_slug and modify action_object_url to contain item AND revision

            ctx.update({'item': obj.data['item']})

            item = Item.objects.get(slug=obj.data.get('item', {}).get('slug'))
            review_document_link = item.get_user_review_url(user=self.request.user, version_slug=obj.action_object.slug)

            ctx.update({'action_object_url': "%s:%s" % (obj.action_object.item.get_absolute_url(),
                                                        review_document_link)})
            ctx.update({'revision_slug': "%s" % obj.action_object.slug})

        return _get_activity_display(ctx, template)


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
