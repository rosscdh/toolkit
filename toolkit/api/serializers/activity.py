# -*- coding: utf-8 -*-
from actstream.models import Action
from rest_framework import serializers

from toolkit.apps.review.models import ReviewDocument

from toolkit.core.services.matter_activity import get_verb_slug

from toolkit.apps.notification import loader, ACTIVITY_TEMPLATES


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
            'actor_name': obj.actor.get_full_name() if obj.actor else None,
            'actor_initials': obj.actor.get_initials() if obj else None,
            'comment': obj.data.get('comment', None),
            'actor_pk': obj.actor.pk,
            'action_object_name': obj.action_object.__unicode__() if obj.action_object else None,
            'action_object_url': None,
            'timestamp': obj.timestamp,
            'timesince': obj.timesince(),
            'message': message,
        }

        if verb_slug in ['revision-added-review-session-comment', 'revision-added-revision-comment']:
            #
            # in the case of the comments we need to do some funky things to get the
            # regular_url from the object
            #
            ctx.update({'item_name': obj.data.get('item', {}).get('name')})

            # get reviewdocument to create the action_object_url
            reviewdocument_object = ReviewDocument.objects.get(slug=reviewdocument.get('slug')) if reviewdocument else None

            # getting the reviewer_object is ONLY possible if we have a review_copy. otherwise the reviewers are empty
            reviewer_object = reviewdocument_object.reviewers.first() if reviewdocument_object else None

            ctx.update({'reviewer_name': reviewer_object.get_full_name() if reviewer_object else None})
            ctx.update({'action_object_url': reviewdocument_object.get_regular_url() if reviewdocument else None})
            ctx.update({'revision_slug': "%s" % obj.action_object.slug})
        else:
            #
            # its not a special attention activity item and we can just process it normally
            #
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
