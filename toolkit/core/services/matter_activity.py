# -*- coding: utf-8 -*-
from ..signals.activity_listener import send_activity_log

from toolkit.api.serializers import ItemSerializer
from toolkit.api.serializers.user import LiteUserSerializer

import datetime


class MatterActivityEventService(object):
    """
    Service to handle events relating to the mater
    """
    def __init__(self, matter, **kwargs):
        self.matter = matter

    def _create_activity(self, actor, verb, action_object, **kwargs):
        activity_kwargs = {
            'actor': actor,
            'verb': verb,
            'action_object': action_object,
            'target': self.matter,
            'message': kwargs.get('message', None),
            'user': None if not kwargs.get('user', None) else LiteUserSerializer(kwargs.get('user')).data,
            'item': None if not kwargs.get('item', None) else ItemSerializer(kwargs.get('item')).data,
            'comment': kwargs.get('comment', None),
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

    def added_matter_participant(self, item, adding_user, added_user):
        message = u'%s added %s as a participant of %s' % (adding_user, added_user, item.matter)
        self._create_activity(actor=adding_user, verb=u'added participant', action_object=item.matter, message=message,
                              user=added_user)

    def removed_matter_participant(self, item, removing_user, removed_user):
        message = u'%s removed %s as a participant of %s' % (removing_user, removed_user, item.matter)
        self._create_activity(actor=removing_user, verb=u'edited', action_object=item.matter, message=message,
                              user=removed_user)
    #
    # Item focused events
    #

    def created_item(self, user, item):
        self._create_activity(actor=user, verb=u'created', action_object=item)

    def item_rename(self, user, item, previous_name):
        message = u'%s renamed item from %s to %s' % (user, item, previous_name, item.name)
        self._create_activity(actor=user, verb=u'renamed', action_object=item, item=item, message=message, previous_name=previous_name)

    def item_change_status(self, user, item, previous_status):
        current_status = item.display_status
        message = u'%s changed the status item from %s to %s' % (user, item, previous_status, current_status)
        self._create_activity(actor=user, verb=u'changed the status', action_object=item, item=item, message=message, current_status=current_status, previous_status=previous_status)

    def item_close(self, user, item):
        message = u'%s closed %s' % (user, item)
        self._create_activity(actor=user, verb=u'closed', action_object=item, item=item, message=message)

    def item_reopened(self, user, item):
        message = u'%s reopened %s' % (user, item)
        self._create_activity(actor=user, verb=u'reopened', action_object=item, item=item, message=message)

    def add_item_comment(self, user, item, comment):
        message = '%s commented on %s' % (user, item)
        self._create_activity(actor=user, verb=u'commented', action_object=item, message=message, comment=comment)

    #
    # Revisions
    #

    def created_revision(self, user, item, revision):
        message = u'%s created a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'created', action_object=revision, item=item, message=message, filename=revision.name, date_created=revision.date_created)

    def deleted_revision(self, user, item, revision):
        message = u'%s destroyed a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted', action_object=revision, item=item, message=message, filename=revision.name, date_created=revision.date_created)

    def request_user_upload_revision(self, item, adding_user, added_user):
        message = u'%s requested %s provide a document on %s' % (adding_user, added_user, item)
        self._create_activity(actor=adding_user, verb=u'provide a document', action_object=item, message=message,
                              user=added_user)

    def cancel_user_upload_revision_request(self, item, removing_user, removed_user):
        message = u'%s canceled their request for %s to provide a document on %s' % (removing_user, removed_user, item)
        self._create_activity(actor=removing_user, verb=u'canceled their request for a document', action_object=item, message=message,
                              user=removed_user)

    def user_uploaded_revision(self, item, user, revision):
        message = u'%s uploaded a document named %s for %s' % (user, revision.name, item)
        self._create_activity(actor=user, verb=u'uploaded a document', action_object=item, message=message,
                              revision=revision, filename=revision.name, date_created=revision.date_created)

    def add_revision_comment(self, user, revision, comment):
        message = '%s commented on %s' % (user, revision)
        self._create_activity(actor=user, verb=u'commented', action_object=revision.item, message=message, comment=comment)

    #
    # Review requests
    #
    def added_user_as_reviewer(self, item, adding_user, added_user):
        message = u'%s added %s as reviewer for %s' % (adding_user, added_user, item)
        self._create_activity(actor=adding_user, verb=u'edited', action_object=item, message=message,
                              user=added_user)

    def removed_user_as_reviewer(self, item, removing_user, removed_user):
        message = u'%s removed %s as reviewer for %s' % (removing_user, removed_user, item)
        self._create_activity(actor=removing_user, verb=u'edited', action_object=item, message=message,
                              user=removed_user)

    def user_viewed_revision(self, item, user, revision):
        message = u'%s viewed revision %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'viewed revision', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug, date_created=datetime.datetime.utcnow())

    def user_commented_on_revision(self, item, user, revision, comment):
        message = u'%s commented on %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'commented on revision', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug, date_created=datetime.datetime.utcnow(),
                              comment=comment)

    def user_revision_review_complete(self, item, user, revision):
        message = u'%s completed their review of %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'completed review', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug, date_created=datetime.datetime.utcnow())
