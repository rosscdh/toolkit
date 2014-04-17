# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify

from .analytics import AtticusFinch
from ..signals.activity_listener import send_activity_log

import datetime

import logging
logger = logging.getLogger('django.request')


def get_verb_slug(action_object, verb):
    verb_slug = slugify(action_object.__class__.__name__) + '-' + slugify(verb)
    logger.debug('possible verb_slug: "%s"' % verb_slug)

    #print(verb_slug)
    # with open('/tmp/verb_slugs.log', 'a') as f:
    #     f.write(verb_slug + '\r\n')

    return verb_slug


class MatterActivityEventService(object):
    """
    Service to handle events relating to the mater

    Known Verb Slugs
    ----------

    Matters
    =======

    workspace-added-participant
    workspace-created
    workspace-deleted
    workspace-edited
    workspace-removed-participant
    workspace-stopped-participating

    Items
    =======

    item-added-revision-comment
    item-canceled-their-request-for-a-document
    item-changed-the-status
    item-closed

    item-comment-created
    item-comment-deleted
    item-commented
    item-created
    item-edited
    item-deleted-revision-comment
    item-invited-reviewer
    item-provide-a-document

    item-renamed
    item-reopened
    item-reopened
    item-viewed-revision
    item-completed-review
    item-completed-all-reviews

    itemrequestrevisionview-provide-a-document

    Revisions
    =======

    revision-comment-created
    revision-added-revision-comment     #crocodoc annotation
    revision-added-review-session-comment     #crocodoc annotation for user NOT in revision.item.participants
    revision-comment-deleted
    revision-created
    revision-deleted

    """
    def __init__(self, matter, **kwargs):
        self.matter = matter
        self.analytics = AtticusFinch()

    def _create_activity(self, actor, verb, action_object, **kwargs):
        from toolkit.api.serializers import ItemSerializer  # must be imported due to cyclic with this class being imported in Workspace.models
        from toolkit.api.serializers.user import LiteUserSerializer  # must be imported due to cyclic with this class being imported in Workspace.models

        activity_kwargs = {
            'actor': actor,
            'verb': verb,
            'verb_slug': get_verb_slug(action_object, verb),  # used to help identify the item and perhaps css class'verb_slug': slugify(verb)
            'action_object': action_object,
            'target': self.matter,
            'message': kwargs.get('message', None),
            'override_message': kwargs.get('override_message', None),
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
        self.analytics.event('matter.created', user=lawyer, **{
            'firm_name': lawyer.profile.firm_name,
            'matter_pk': self.matter.pk
        })

    def deleted_matter(self, lawyer):
        override_message = u'%s deleted the %s matter' % (lawyer, self.matter)
        self._create_activity(actor=lawyer, verb=u'deleted',
                              action_object=self.matter,
                              override_message=override_message)
        self.analytics.event('matter.deleted', user=lawyer, **{
            'firm_name': lawyer.profile.firm_name,
            'matter_pk': self.matter.pk
        })

    def added_matter_participant(self, adding_user, added_user, **kwargs):
        if adding_user.pk != added_user.pk:
            override_message = u'%s added a new member to %s' % (adding_user, matter)
            self._create_activity(actor=adding_user, verb=u'added participant', action_object=matter,
                                  override_message=override_message, user=added_user)
            self.analytics.event('matter.participant.added', user=adding_user, **{
                'matter_pk': self.matter.pk,
                'participant': added_user.get_full_name(),
                'participant_type': added_user.profile.type,
            })

    def removed_matter_participant(self, removing_user, removed_user, **kwargs):
        override_message = u'%s removed %s as a participant of %s' % (removing_user, removed_user, self.matter)
        self._create_activity(actor=removing_user, verb=u'removed participant', action_object=self.matter,
                              override_message=override_message, user=removed_user)

    def user_stopped_participating(self, user):
        override_message = u'%s stopped participating in %s' % (user, self.matter)
        self._create_activity(actor=user, verb=u'stopped participating', action_object=self.matter,
                              override_message=override_message, user=user)

    #
    # Item focused events
    #
    def item_created(self, user, item):
        self._create_activity(actor=user, verb=u'created', action_object=item)
        self.analytics.event('item.created', user=user, **{
            'matter_pk': self.matter.pk
        })

    def item_rename(self, user, item, previous_name):
        override_message = u'%s renamed item from %s to %s' % (user, previous_name, item.name)
        self._create_activity(actor=user, verb=u'renamed', action_object=item, item=item,
                              override_message=override_message, previous_name=previous_name)

    def item_changed_status(self, user, item, previous_status):
        current_status = item.display_status
        override_message = u'%s set %s to %s' % (user, item, current_status)
        # override_message = u'%s changed the status of %s from %s to %s' % (user, item, previous_status, current_status)
        self._create_activity(actor=user, verb=u'changed the status', action_object=item, item=item,
                              override_message=override_message, current_status=current_status,
                              previous_status=previous_status)

    def item_closed(self, user, item):
        override_message = u'%s closed %s' % (user, item)
        self._create_activity(actor=user, verb=u'closed', action_object=item, item=item,
                              override_message=override_message)

    def item_reopened(self, user, item):
        override_message = u'%s reopened %s' % (user, item)
        self._create_activity(actor=user, verb=u'reopened', action_object=item, item=item,
                              override_message=override_message)

    def add_item_comment(self, user, item, comment):
        override_message = '%s commented on %s "%s"' % (user, item, comment)
        self._create_activity(actor=user, verb=u'commented', action_object=item, override_message=override_message,
                              comment=comment)

    def delete_item_comment(self, user, item):
        override_message = '%s deleted a comment on %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted comment', action_object=item,
                              override_message=override_message)

    #
    # Revisions
    #

    def created_revision(self, user, item, revision):
        override_message = u'%s added a file to %s' % (user, item)
        self._create_activity(actor=user, verb=u'created', action_object=revision, item=item,
                              override_message=override_message, filename=revision.name,
                              date_created=revision.date_created)

        self.analytics.event('revision.create', user=user, **{
            'matter_pk': self.matter.pk
        })

    def deleted_revision(self, user, item, revision):
        override_message = u'%s destroyed a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted', action_object=revision, item=item,
                              override_message=override_message, filename=revision.name,
                              date_created=revision.date_created)

    def request_user_upload_revision(self, item, adding_user, added_user):
        override_message = u'%s requested a file from %s for %s' % (adding_user, added_user, item)
        # override_message = u'%s requested %s provide a document on %s' % (adding_user, added_user, item)
        self._create_activity(actor=adding_user, verb=u'provide a document', action_object=item,
                              override_message=override_message, user=added_user)
        self.analytics.event('revision.upload.request', user=adding_user, **{
            'matter_pk': self.matter.pk,
            'requestee': added_user.get_full_name(),
            'requestee_type': added_user.profile.type,
            'requestor': added_user.get_full_name(),
            'requestor_type': added_user.profile.type
        })

    def cancel_user_upload_revision_request(self, item, removing_user, removed_user):
        override_message = u'%s canceled their request for %s to provide a document on %s' % (removing_user,
                                                                                              removed_user, item)
        self._create_activity(actor=removing_user, verb=u'canceled their request for a document', action_object=item,
                              override_message=override_message, user=removed_user)

    def user_uploaded_revision(self, user, item, revision):
        override_message = u'%s uploaded a document named %s for %s' % (user, revision.name, item)
        self._create_activity(actor=user, verb=u'uploaded a document', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              date_created=revision.date_created)
        self.analytics.event('revision.upload.provided', user=user, **{
            'matter_pk': self.matter.pk
        })

    def add_revision_comment(self, user, revision, comment):
        override_message = '%s annotated %s in %s' % (user, revision.slug, revision.item)
        self._create_activity(actor=user, verb=u'added revision comment', action_object=revision,
                              override_message=override_message, comment=comment, item=revision.item)
        self.analytics.event('revision.comment.added', user=user, **{
            'item_pk': revision.item.pk,
            'matter_pk': self.matter.pk
        })

    def add_review_copy_comment(self, user, revision, comment):
        override_message = '%s annotated %s (review comment) in %s' % (user, revision.slug, revision.item)
        self._create_activity(actor=user, verb=u'added review-session comment', action_object=revision,
                              override_message=override_message, comment=comment, item=revision.item)
        self.analytics.event('revision.comment.added', user=user, **{
            'item_pk': revision.item.pk,
            'matter_pk': revision.item.matter.pk
        })

    def delete_revision_comment(self, user, revision):
        override_message = '%s deleted a comment on %s' % (user, revision)
        self._create_activity(actor=user, verb=u'deleted revision comment', action_object=revision,
                              override_message=override_message, item=revision.item)

    #
    # Review requests
    #

    def invite_user_as_reviewer(self, item, inviting_user, invited_user):
        if inviting_user.pk != invited_user:
            override_message = u'%s invited a reviewer to %s' % (inviting_user, item)
            # override_message = u'%s invited %s as reviewer for %s' % (inviting_user, invited_user, item)
            self._create_activity(actor=inviting_user, verb=u'invited reviewer', action_object=item,
                                  override_message=override_message, user=invited_user)
            self.analytics.event('review.request.sent', user=inviting_user, **{
                'invited': invited_user.get_full_name(),
                'invited_type': invited_user.profile.type,
                'item_pk': item.pk,
                'matter_pk': self.matter.pk
            })

    # instead of this we now use the newly created invite_user_as_reviewer
    # def added_user_as_reviewer(self, item, adding_user, added_user):
    #     override_message = u'%s added %s as reviewer for %s' % (adding_user, added_user, item)
    #     self._create_activity(actor=adding_user, verb=u'added reviewer', action_object=item, override_message=override_message,
    #                           user=added_user)
    #
    # instead of this we now use cancel_user_upload_revision_request() above
    # def removed_user_as_reviewer(self, item, removing_user, removed_user):
    #     override_message = u'%s removed %s as reviewer for %s' % (removing_user, removed_user, item)
    #     self._create_activity(actor=removing_user, verb=u'removed reviewer', action_object=item, override_message=override_message,
    #                           user=removed_user)

    def user_viewed_revision(self, item, user, revision):
        override_message = u'%s viewed revision %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'viewed revision', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.request.viewed', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })

    def user_downloaded_revision(self, item, user, revision):
        override_message = u'%s downloaded revision %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'viewed revision', action_object=revision,
                              override_message=override_message, item=item, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow(), comment=comment)
        self.analytics.event('review.request.comment.added', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })

    def user_revision_review_complete(self, item, user, revision):
        override_message = u'%s completed their review of %s' % (user, revision.slug)
        self._create_activity(actor=user, verb=u'completed review', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.request.completed', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })

    def all_revision_reviews_complete(self, item, revision):
        override_message = u'All of the reviews of %s have been completed' % (item,)
        self._create_activity(actor=self.matter.lawyer, verb=u'completed all reviews', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.all_requests.completed', user=self.matter.lawyer, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })

    #
    # Signing
    #
    def invite_user_as_signer(self, item, inviting_user, invited_user):
        message = u'%s invited %s as signer for %s' % (inviting_user, invited_user, item)
        self._create_activity(actor=inviting_user, verb=u'invited signer', action_object=item, message=message,
                              user=invited_user)
        self.analytics.event('sign.request.sent', user=inviting_user, **{
            'invited': invited_user.get_full_name(),
            'invited_type': invited_user.profile.type,
            'item_pk': item.pk,
            'matter_pk': self.matter.pk
        })

    def user_viewed_signature_request(self, item, user, revision):
        message = u'%s viewed signature request %s (%s) for %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'viewed revision', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug,
                              date_created=datetime.datetime.utcnow())
        self.analytics.event('sign.request.viewed', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })
