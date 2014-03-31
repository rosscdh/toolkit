# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify

from .analytics import AtticusFinch
from ..signals.activity_listener import send_activity_log

import datetime

import logging
logger = logging.getLogger('django.request')


class MatterActivityEventService(object):
    """
    Service to handle events relating to the mater
    """
    def __init__(self, matter, **kwargs):
        self.matter = matter
        self.analytics = AtticusFinch()

    def get_verb_slug(self, action_object, verb):
        verb_slug = slugify(action_object.__class__.__name__) + '-' + slugify(verb)
        logger.debug('possible verb_slug: "%s"' % verb_slug)
        return verb_slug

    def _create_activity(self, actor, verb, action_object, **kwargs):
        from toolkit.api.serializers import ItemSerializer  # must be imported due to cyclic with this class being imported in Workspace.models
        from toolkit.api.serializers.user import LiteUserSerializer  # must be imported due to cyclic with this class being imported in Workspace.models

        activity_kwargs = {
            'actor': actor,
            'verb': verb,
            'verb_slug': self.get_verb_slug(action_object, verb),  # used to help identify the item and perhaps css class'verb_slug': slugify(verb)
            'action_object': action_object,
            'target': self.matter,
            'message': kwargs.get('message', None),
            'user': None if not kwargs.get('user', None) else LiteUserSerializer(kwargs.get('user')).data,
            'item': None if not kwargs.get('item', None) else ItemSerializer(kwargs.get('item')).data,
            'comment': kwargs.get('comment', None),
            'previous_name': kwargs.get('previous_name', None),
            'current_status': kwargs.get('previous_name', None),
            'previous_status': kwargs.get('previous_status', None),
            'filename': kwargs.get('filename', None),
            'date_created': kwargs.get('date_created', None),
            'version': kwargs.get('version', None),
        }
        # @BUSINESSRULE
        # merge our specific extra kwargs passed in
        # with the base activity_kwargs, force the passed in kwargs
        # tobe overriden as they are the foundation of the messaging system
        kwargs.update(activity_kwargs)
        send_activity_log.send(self, **kwargs)

    #
    # Matter
    #
    def created_matter(self, lawyer):
        self._create_activity(actor=lawyer, verb=u'created', action_object=self.matter)
        self.analytics.event('matter.created', distinct_id=lawyer.pk, user=lawyer.get_full_name())

    def added_matter_participant(self, matter, adding_user, added_user):
        message = u'%s added %s as a participant of %s' % (adding_user, added_user, matter)
        self._create_activity(actor=adding_user, verb=u'added participant', action_object=matter, message=message,
                              user=added_user)
        self.analytics.event('matter.participant.added', distinct_id=adding_user.pk, user=adding_user.get_full_name(),
                             participant=added_user.get_full_name(), matter_pk=matter.pk)

        self.analytics.event('matter.participant.added', distinct_id=adding_user.pk, user=adding_user.get_full_name(), participant=added_user.get_full_name(), matter_pk=matter.pk)

    def removed_matter_participant(self, matter, removing_user, removed_user):
        message = u'%s removed %s as a participant of %s' % (removing_user, removed_user, matter)
        self._create_activity(actor=removing_user, verb=u'edited', action_object=matter, message=message,
                              user=removed_user)
    #
    # Item focused events
    #
    def item_created(self, user, item):
        self._create_activity(actor=user, verb=u'created', action_object=item)
        self.analytics.event('item.created', distinct_id=user.pk, user=user.get_full_name())

    def item_rename(self, user, item, previous_name):
        message = u'%s renamed item from %s to %s' % (user, previous_name, item.name)
        self._create_activity(actor=user, verb=u'renamed', action_object=item, item=item, message=message,
                              previous_name=previous_name)

    def item_changed_status(self, user, item, previous_status):
        current_status = item.display_status
        message = u'%s changed the status of %s from %s to %s' % (user, item, previous_status, current_status)
        self._create_activity(actor=user, verb=u'changed the status', action_object=item, item=item, message=message,
                              current_status=current_status, previous_status=previous_status)

    def item_closed(self, user, item):
        message = u'%s closed %s' % (user, item)
        self._create_activity(actor=user, verb=u'closed', action_object=item, item=item, message=message)

    def item_reopened(self, user, item):
        message = u'%s reopened %s' % (user, item)
        self._create_activity(actor=user, verb=u'reopened', action_object=item, item=item, message=message)

    def add_item_comment(self, user, item, comment):
        message = '%s commented on %s' % (user, item)
        self._create_activity(actor=user, verb=u'commented', action_object=item, message=message, comment=comment)

    def delete_item_comment(self, user, item):
        message = '%s deleted a comment on %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted comment', action_object=item, message=message)

    #
    # Revisions
    #

    def created_revision(self, user, item, revision):
        message = u'%s created a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'created', action_object=revision, item=item, message=message,
                              filename=revision.name, date_created=revision.date_created)

    def deleted_revision(self, user, item, revision):
        message = u'%s destroyed a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted', action_object=revision, item=item, message=message,
                              filename=revision.name, date_created=revision.date_created)

    def request_user_upload_revision(self, item, adding_user, added_user):
        message = u'%s requested %s provide a document on %s' % (adding_user, added_user, item)
        self._create_activity(actor=adding_user, verb=u'provide a document', action_object=item, message=message,
                              user=added_user)

    def cancel_user_upload_revision_request(self, item, removing_user, removed_user):
        message = u'%s canceled their request for %s to provide a document on %s' % (removing_user, removed_user, item)
        self._create_activity(actor=removing_user, verb=u'canceled their request for a document', action_object=item,
                              message=message, user=removed_user)

    def user_uploaded_revision(self, user, item, revision):
        message = u'%s uploaded a document named %s for %s' % (user, revision.name, item)
        self._create_activity(actor=user, verb=u'uploaded a document', action_object=item, message=message,
                              revision=revision, filename=revision.name, date_created=revision.date_created)

    def add_revision_comment(self, user, revision, comment):
        message = '%s commented on %s' % (user, revision)
        self._create_activity(actor=user, verb=u'added revision comment', action_object=revision, message=message,
                              comment=comment, item=revision.item)

    def delete_revision_comment(self, user, revision):
        message = '%s deleted a comment on %s' % (user, revision)
        self._create_activity(actor=user, verb=u'deleted revision comment', action_object=revision, message=message,
                              item=revision.item)

    #
    # Review requests
    #

    def invite_user_as_reviewer(self, item, inviting_user, invited_user):
        message = u'%s invited %s as reviewer for %s' % (inviting_user, invited_user, item)
        self._create_activity(actor=inviting_user, verb=u'invited reviewer', action_object=item, message=message,
                              user=invited_user)

    # instead of this we now use the newly created invite_user_as_reviewer
    # def added_user_as_reviewer(self, item, adding_user, added_user):
    #     message = u'%s added %s as reviewer for %s' % (adding_user, added_user, item)
    #     self._create_activity(actor=adding_user, verb=u'added reviewer', action_object=item, message=message,
    #                           user=added_user)
    #
    # instead of this we now use cancel_user_upload_revision_request() above
    # def removed_user_as_reviewer(self, item, removing_user, removed_user):
    #     message = u'%s removed %s as reviewer for %s' % (removing_user, removed_user, item)
    #     self._create_activity(actor=removing_user, verb=u'removed reviewer', action_object=item, message=message,
    #                           user=removed_user)

    def user_viewed_revision(self, item, user, revision):
        message = u'%s viewed revision %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'viewed revision', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug,
                              date_created=datetime.datetime.utcnow())

    def user_commented_on_revision(self, item, user, revision, comment):
        message = u'%s commented on %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'commented on revision', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug,
                              date_created=datetime.datetime.utcnow(),
                              comment=comment)

    def user_revision_review_complete(self, item, user, revision):
        message = u'%s completed their review of %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'completed review', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug,
                              date_created=datetime.datetime.utcnow())
