# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify

from ..signals.activity_listener import send_activity_log

import datetime


class MatterActivityEventService(object):
    """
    Service to handle events relating to the mater
    """
    def __init__(self, matter, **kwargs):
        self.matter = matter

    def _create_activity(self, actor, verb, action_object, **kwargs):
        from toolkit.api.serializers import ItemSerializer  # must be imported due to cyclic with this class being imported in Workspace.models
        from toolkit.api.serializers.user import LiteUserSerializer  # must be imported due to cyclic with this class being imported in Workspace.models

        activity_kwargs = {
            'actor': actor,
            'verb': verb,
            'verb_slug': slugify(verb), # used to help identify the item and perhaps css class
            'action_object': action_object,
            'target': self.matter,
            'log_message': kwargs.get('log_message', None),
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
        log_message = u'%s added %s as a participant of %s' % (adding_user, added_user, item.matter)
        self._create_activity(actor=adding_user, verb=u'added participant', action_object=item.matter, log_message=log_message,
                              user=added_user)

    def removed_matter_participant(self, item, removing_user, removed_user):
        log_message = u'%s removed %s as a participant of %s' % (removing_user, removed_user, item.matter)
        self._create_activity(actor=removing_user, verb=u'edited', action_object=item.matter, log_message=log_message,
                              user=removed_user)
    #
    # Item focused events
    #

    def created_item(self, user, item):
        self._create_activity(actor=user, verb=u'created', action_object=item)

    def item_rename(self, user, item, previous_name):
        log_message = u'%s renamed item from %s to %s' % (user, item, previous_name, item.name)
        self._create_activity(actor=user, verb=u'renamed', action_object=item, item=item, log_message=log_message, previous_name=previous_name)

    def item_change_status(self, user, item, previous_status):
        current_status = item.display_status
        log_message = u'%s changed the status item from %s to %s' % (user, item, previous_status, current_status)
        self._create_activity(actor=user, verb=u'changed the status', action_object=item, item=item, log_message=log_message, current_status=current_status, previous_status=previous_status)

    def item_close(self, user, item):
        log_message = u'%s closed %s' % (user, item)
        self._create_activity(actor=user, verb=u'closed', action_object=item, item=item, log_message=log_message)

    def item_reopened(self, user, item):
        log_message = u'%s reopened %s' % (user, item)
        self._create_activity(actor=user, verb=u'reopened', action_object=item, item=item, log_message=log_message)

    def add_item_comment(self, user, item, comment):
        log_message = '%s commented on %s' % (user, item)
        self._create_activity(actor=user, verb=u'commented', action_object=item, log_message=log_message, comment=comment)

    def delete_item_comment(self, user, item):
        log_message = '%s deleted a comment on %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted comment', action_object=item, log_message=log_message)

    #
    # Revisions
    #

    def created_revision(self, user, item, revision):
        log_message = u'%s created a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'created', action_object=revision, item=item, log_message=log_message, filename=revision.name, date_created=revision.date_created)

    def deleted_revision(self, user, item, revision):
        log_message = u'%s destroyed a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted', action_object=revision, item=item, log_message=log_message, filename=revision.name, date_created=revision.date_created)

    def request_user_upload_revision(self, item, adding_user, added_user):
        log_message = u'%s requested %s provide a document on %s' % (adding_user, added_user, item)
        self._create_activity(actor=adding_user, verb=u'provide a document', action_object=item, log_message=log_message,
                              user=added_user)

    def cancel_user_upload_revision_request(self, item, removing_user, removed_user):
        log_message = u'%s canceled their request for %s to provide a document on %s' % (removing_user, removed_user, item)
        self._create_activity(actor=removing_user, verb=u'canceled their request for a document', action_object=item, log_message=log_message,
                              user=removed_user)

    def user_uploaded_revision(self, item, user, revision):
        log_message = u'%s uploaded a document named %s for %s' % (user, revision.name, item)
        self._create_activity(actor=user, verb=u'uploaded a document', action_object=item, log_message=log_message,
                              revision=revision, filename=revision.name, date_created=revision.date_created)

    def add_revision_comment(self, user, revision, comment):
        log_message = '%s commented on %s' % (user, revision)
        self._create_activity(actor=user, verb=u'commented', action_object=revision.item, log_message=log_message, comment=comment)

    def delete_revision_comment(self, user, revision):
        log_message = '%s deleted a comment on %s' % (user, revision)
        self._create_activity(actor=user, verb=u'deleted comment', action_object=revision.item, log_message=log_message)

    #
    # Review requests
    #
    def added_user_as_reviewer(self, item, adding_user, added_user):
        log_message = u'%s added %s as reviewer for %s' % (adding_user, added_user, item)
        self._create_activity(actor=adding_user, verb=u'edited', action_object=item, log_message=log_message,
                              user=added_user)

    def removed_user_as_reviewer(self, item, removing_user, removed_user):
        log_message = u'%s removed %s as reviewer for %s' % (removing_user, removed_user, item)
        self._create_activity(actor=removing_user, verb=u'edited', action_object=item, log_message=log_message,
                              user=removed_user)

    def user_viewed_revision(self, item, user, revision):
        log_message = u'%s viewed revision %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'viewed revision', action_object=item, log_message=log_message,
                              revision=revision, filename=revision.name, version=revision.slug, date_created=datetime.datetime.utcnow())

    def user_commented_on_revision(self, item, user, revision, comment):
        log_message = u'%s commented on %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'commented on revision', action_object=item, log_message=log_message,
                              revision=revision, filename=revision.name, version=revision.slug, date_created=datetime.datetime.utcnow(),
                              comment=comment)

    def user_revision_review_complete(self, item, user, revision):
        log_message = u'%s completed their review of %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'completed review', action_object=item, log_message=log_message,
                              revision=revision, filename=revision.name, version=revision.slug, date_created=datetime.datetime.utcnow())
