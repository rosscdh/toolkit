# -*- coding: utf-8 -*-
from django.template import loader

from actstream.models import Action
from rest_framework import serializers

from toolkit.api.serializers.item import LiteItemSerializer
from toolkit.api.serializers.user import LiteUserSerializer
from toolkit.apps.review.models import ReviewDocument
from toolkit.core.item.models import Item

from toolkit.core.services.matter_activity import get_verb_slug


ACTIVITY_TEMPLATES = {
    'default': loader.get_template('activity/default.html'),
    'item-commented': loader.get_template('activity/item_comment.html'),
    'revision-added-review-session-comment': loader.get_template('activity/review_session_comment.html'),
    'revision-added-revision-comment': loader.get_template('activity/revision_comment.html'),
}


class MatterActivitySerializer(serializers.HyperlinkedModelSerializer):
    event = serializers.SerializerMethodField('get_event')

    class Meta:
        model = Action
        lookup_field = 'id'
        fields = ('id', 'event', 'timestamp')  # timestamp can possibly be removed (if ONLY event is shown in template)

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs and 'request' in kwargs['context']:
            self.request = kwargs['context']['request']
        super(MatterActivitySerializer, self).__init__(*args, **kwargs)

    """
    helper methods for get_event() which creates an html-representation of an Action
    """
    @staticmethod
    def _get_template(verb_slug):
        return ACTIVITY_TEMPLATES.get(verb_slug, ACTIVITY_TEMPLATES.get('default'))

    def _get_context(self, obj, verb_slug):
        """
        'comment' gets set IF it is a revision- or item-comment
        'message' is set otherwise

        'item' is only set if it is a revision-comment. no other activity has an item.
        """

        message = obj.data.get('override_message', None)
        if message is None:
            message = u"%s %s %s" % (obj.actor, obj.verb, obj.action_object)

        reviewdocument = obj.data.get('reviewdocument', None)

        ctx = {
            'actor_name': obj.actor.__unicode__() if obj else None,
            'actor_initials': obj.actor.get_initials() if obj else None,
            'comment': obj.data.get('comment', None),
            'actor_pk': obj.actor.pk,
            'action_object_name': obj.action_object.__unicode__() if obj else None,
            'action_object_url': None,
            'timestamp': obj.timestamp,
            'timesince': obj.timesince(),
            'message': message,
        }

        if verb_slug in ['revision-added-review-session-comment', 'revision-added-revision-comment']:
            # exception for revision-commens:
            # add item, revision_slug and modify action_object_url to contain item AND revision

            # ctx.update({'item': obj.data['item']})
            ctx.update({'item_name': obj.data.get('item', {}).get('name')})

            # item = Item.objects.get(slug=obj.data.get('item', {}).get('slug'))
            # ctx.update({'action_object_url': item.get_full_user_review_url(user=self.request.user,
            #                                                                version_slug=obj.action_object.slug)})

            # get reviewdocument to create the action_object_url
            reviewdocument_object = ReviewDocument.objects.get(slug=reviewdocument.get('slug')) if reviewdocument else None
            ctx.update({'action_object_url': reviewdocument_object.get_regular_url() if reviewdocument else None})
            ctx.update({'revision_slug': "%s" % obj.action_object.slug})
        else:
            if obj.action_object and hasattr(obj.action_object, 'get_absolute_url'):
                ctx.update({'action_object_url': obj.action_object.get_absolute_url()})

        return ctx

    def get_event(self, obj):
        """
        Is used on notifications-page and works similar to notice_tags:
        - load verb_slug and decide on this (-> ACTIVITY_TEMPLATES) which template is used
        - fill ctx with needed data
        """
        verb_slug = get_verb_slug(obj.action_object, obj.verb)

        template = self._get_template(verb_slug)
        context = loader.Context(self._get_context(obj, verb_slug))

        # render the template with passed in context
        return template.render(context)


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
