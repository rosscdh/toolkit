# -*- coding: utf-8 -*-
from django.utils import timezone
from django.template.defaultfilters import slugify

from toolkit.tasks import run_task
from toolkit.apps.notification.tasks import realtime_matter_event

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
    workspace-export-started
    workspace-export-finished
    workspace-export-downloaded

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
    serializers = {}  # due to cyclic imports we have to be sneaky here

    def __init__(self, matter, **kwargs):
        self.matter = matter
        self.analytics = AtticusFinch()

        #
        # Cleverly store serializers at the class level
        # to avoid the crappy cyclic import errors
        #
        if not self.serializers: # if we have not set them already
            from toolkit.api.serializers import ItemSerializer  # must be imported due to cyclic with this class being imported in Workspace.models
            from toolkit.api.serializers.user import LiteUserSerializer  # must be imported due to cyclic with this class being imported in Workspace.models
            from toolkit.api.serializers import ReviewSerializer

            self.serializers['ItemSerializer'] = ItemSerializer
            self.serializers['LiteUserSerializer'] = LiteUserSerializer
            self.serializers['ReviewSerializer'] = ReviewSerializer

    def _create_activity(self, actor, verb, action_object, **kwargs):
        """
        Primary collated objects to be sent for processing
        """
        activity_kwargs = {
            'actor': actor,
            'verb': verb,
            'verb_slug': get_verb_slug(action_object, verb),  # used to help identify the item and perhaps css class'verb_slug': slugify(verb)
            'action_object': action_object,
            'target': self.matter,
            'message': kwargs.get('message', None),
            'override_message': kwargs.get('override_message', None),
            'user': None if not kwargs.get('user', None) else self.serializers.get('LiteUserSerializer')(kwargs.get('user')).data,
            'item': None if not kwargs.get('item', None) else self.serializers.get('ItemSerializer')(kwargs.get('item')).data,
            'reviewdocument': None if not kwargs.get('reviewdocument', None) else self.serializers.get('ReviewSerializer')(kwargs.get('reviewdocument')).data,
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

        self.update_matter_date_modified()

    def update_matter_date_modified(self):
        """
        Update the matter date_modified on every event
        @NB we use the .update() on a queryset here as this does not then fire
        the pre_save and post_save signals thus is more efficient
        """
        ## make utcnow timezone aware so we can compare dates
        date_time = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        time_ago_rage = date_time - datetime.timedelta(minutes=-5)

        date_last_modified = self.matter.date_modified.replace(tzinfo=timezone.utc)

        # if the matter date_modified is older than 5 minutes ago perform this update
        if date_last_modified < time_ago_rage:
            self.matter.__class__.objects.filter(pk=self.matter.pk).update(date_modified=date_time)


    def realtime_event(self, event, obj, ident, from_user=None, **kwargs):
        """
        Send a realtime pusher event
        Semi-ironic as we need to have a fake delay to ensure that the update gets through
        can perhaps be solved with chaining http://docs.celeryproject.org/en/latest/userguide/canvas.html#chains
        """
        from_ident = None
        # only set it if we have a from_user
        if hasattr(from_user, 'username'):
            from_ident = from_user.username
        #
        # Run async realtime_matter_event pusher
        #
        run_task(realtime_matter_event, matter=self.matter,
                                        event=event, obj=obj, ident=ident,
                                        from_ident=from_ident,
                                        countdown=5,  # Delay by set 5 seconds before sending event
                                        **kwargs)
    #
    # Matter
    #
    def created_matter(self, lawyer):
        # is called from matters post_save with matter.lawyer in toolkit/apps/workspace/signals.py
        # because of toolkit.api.views.matter.MatterEndpoint#pre_save this MUST be the creating lawyer
        self._create_activity(actor=lawyer, verb=u'created', action_object=self.matter)
        self.analytics.event('matter.created', user=lawyer, **{
            'firm_name': lawyer.profile.firm_name,
            'matter_pk': self.matter.pk
        })

    def deleted_matter(self, lawyer):
        # is called from matters post_delete with matter.lawyer in toolkit/apps/workspace/signals.py
        # because of toolkit.apps.matter.services.matter_removal.MatterRemovalService#process this MUST be the deleting user
        override_message = u'%s deleted the %s matter' % (lawyer, self.matter)
        self._create_activity(actor=lawyer, verb=u'deleted',
                              action_object=self.matter,
                              override_message=override_message)
        self.analytics.event('matter.deleted', user=lawyer, **{
            'firm_name': lawyer.profile.firm_name,
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='delete', obj=self.matter, ident=self.matter.slug, from_user=lawyer, detail='deleted matter')

    def added_matter_participant(self, adding_user, added_user, **kwargs):
        # is called from toolkit/apps/matter/signals.py#PARTICIPANT_ADDED
        if adding_user.pk != added_user.pk:
            override_message = u'%s added %s as a new member to %s' % (adding_user, added_user, self.matter)
            self._create_activity(actor=adding_user, verb=u'added participant', action_object=self.matter,
                                  override_message=override_message, user=added_user)
            self.analytics.event('matter.participant.added', user=adding_user, **{
                'matter_pk': self.matter.pk,
                'participant': added_user.get_full_name(),
                'participant_type': added_user.profile.type,
            })

    def removed_matter_participant(self, removing_user, removed_user, **kwargs):
        # is called from toolkit/apps/matter/signals.py#PARTICIPANT_DELETED
        if removing_user != removed_user:
            override_message = u'%s removed %s as a participant of %s' % (removing_user, removed_user, self.matter)
            self._create_activity(actor=removing_user, verb=u'removed participant', action_object=self.matter,
                                  override_message=override_message, user=removed_user)


    def user_stopped_participating(self, user):
        # is called from toolkit/apps/matter/signals.py#USER_STOPPED_PARTICIPATING
        override_message = u'%s stopped participating in %s' % (user, self.matter)
        self._create_activity(actor=user, verb=u'stopped participating', action_object=self.matter,
                              override_message=override_message, user=user)

    def started_matter_export(self, user):
        # toolkit.apps.matter.mixins.MatterExportMixin#export_matter
        override_message = u'%s started export of %s' % (user, self.matter)
        self._create_activity(actor=user, verb=u'export started', action_object=self.matter,
                              override_message=override_message)

    def matter_export_finished(self, user):
        # toolkit.apps.matter.services.matter_export.MatterExportService#conclude
        override_message = u'The export of %s for %s has been completed' % (self.matter, user)
        self._create_activity(actor=user, verb=u'export finished', action_object=self.matter,
                              override_message=override_message)

    def user_downloaded_exported_matter(self, user):
        # is called from toolkit/apps/matter/signals.py#USER_DOWNLOADED_EXPORTED_MATTER
        override_message = u'%s downloaded %s' % (user, self.matter)
        self._create_activity(actor=user, verb=u'export downloaded', action_object=self.matter,
                              override_message=override_message)


    #
    # Item focused events
    #
    def item_created(self, user, item):
        # toolkit.api.views.item.MatterItemsView#post_save
        self._create_activity(actor=user, verb=u'created', action_object=item)
        self.analytics.event('item.created', user=user, **{
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='create', obj=item, ident=item.slug, from_user=user, detail='created item')

    def item_rename(self, user, item, previous_name):
        # toolkit.api.views.item.MatterItemView#pre_save
        override_message = u'%s renamed %s to %s' % (user, previous_name, item.name)
        self._create_activity(actor=user, verb=u'renamed', action_object=item, item=item,
                              override_message=override_message, previous_name=previous_name)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='updated item')

    def item_changed_status(self, user, item, previous_status):
        # toolkit.api.views.item.MatterItemView#pre_save
        current_status = item.display_status
        override_message = u'%s set %s to %s' % (user, item, current_status)
        # override_message = u'%s changed the status of %s from %s to %s' % (user, item, previous_status, current_status)
        self._create_activity(actor=user, verb=u'changed the status', action_object=item, item=item,
                              override_message=override_message, current_status=current_status,
                              previous_status=previous_status)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='updated item')

    def item_closed(self, user, item):
        # toolkit.api.views.item.MatterItemView#pre_save
        override_message = u'%s closed %s' % (user, item)
        self._create_activity(actor=user, verb=u'closed', action_object=item, override_message=override_message)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='updated item')

    def item_reopened(self, user, item):
        # toolkit.api.views.item.MatterItemView#pre_save
        override_message = u'%s reopened %s' % (user, item)
        self._create_activity(actor=user, verb=u'reopened', action_object=item, override_message=override_message)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='updated item')

    def item_deleted(self, user, item):
        # toolkit.api.views.item.MatterItemView#pre_save
        override_message = u'%s deleted %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted', action_object=item, override_message=override_message)
        self.realtime_event(event='delete', obj=item, ident=item.slug, from_user=user, detail='deleted item')

    def add_item_comment(self, user, item, comment):
        # toolkit.api.views.comment.ItemCommentEndpoint#create
        override_message = u'%s commented on %s "%s"' % (user, item, comment)
        self._create_activity(actor=user, verb=u'commented', action_object=item, override_message=override_message,
                              comment=comment)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='updated item comment')

    def delete_item_comment(self, user, item):
        # unused
        override_message = u'%s deleted a comment on %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted comment', action_object=item,
                              override_message=override_message)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='updated item')

    #
    # Tasks
    #
    def added_task(self, user, item, task):
        override_message = u'%s added a task "%s" on %s' % (user, task, item)
        self._create_activity(actor=user, verb=u'task-added', action_object=item, override_message=override_message)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='created item task', task_slug=str(task.slug))

    def deleted_task(self, user, item, task):
        override_message = u'%s deleted the task "%s" on %s' % (user, task, item)
        self._create_activity(actor=user, verb=u'task-deleted', action_object=item, override_message=override_message)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='deleted item task', task_slug=str(task.slug))

    def task_completed(self, user, item, task):
        override_message = u'%s completed the task "%s" on %s' % (user, task, item)
        self._create_activity(actor=user, verb=u'task-completed', action_object=item, override_message=override_message)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='completed item task', task_slug=str(task.slug))

    def task_reopened(self, user, item, task):
        override_message = u'%s re-opened the previously closed task "%s" on %s' % (user, task, item)
        self._create_activity(actor=user, verb=u'task-reopened', action_object=item, override_message=override_message)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='reopened item task', task_slug=str(task.slug))

    #
    # Revisions
    #

    def created_revision(self, user, item, revision):
        # toolkit.api.views.revision.ItemCurrentRevisionView#create
        override_message = u'%s added a file to %s' % (user, item)
        self._create_activity(actor=user, verb=u'created', action_object=revision, item=item,
                              override_message=override_message, filename=revision.name,
                              date_created=revision.date_created)

        self.analytics.event('revision.create', user=user, **{
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='created revision')

    def deleted_revision(self, user, item, revision):
        # toolkit.api.views.revision.ItemCurrentRevisionView#destroy
        override_message = u'%s destroyed a revision for %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted', action_object=revision, item=item,
                              override_message=override_message, filename=revision.name,
                              date_created=revision.date_created)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='deleted revision')

    def request_user_upload_revision(self, item, adding_user, added_user):
        # toolkit.api.views.revision_request.ItemRequestRevisionView#post_save
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
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=adding_user,
                            detail='requested revision')

    def cancel_user_upload_revision_request(self, item, removing_user, removed_user):
        # toolkit.api.views.item.MatterItemView#pre_save
        # toolkit.api.views.review.ItemRevisionReviewerView#delete
        # toolkit.api.views.sign.ItemRevisionSignerView#delete
        override_message = u'%s canceled their request for %s to provide a document on %s' % (removing_user,
                                                                                              removed_user, item)
        self._create_activity(actor=removing_user, verb=u'canceled their request for a document', action_object=item,
                              override_message=override_message, user=removed_user)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=removing_user,
                            detail='cancel revision request')

    def user_uploaded_revision(self, user, item, revision):
        # toolkit.api.views.revision.ItemCurrentRevisionView#create
        override_message = u'%s uploaded a document named %s for %s' % (user, revision.name, item)
        self._create_activity(actor=user, verb=u'uploaded a document', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              date_created=revision.date_created)
        self.analytics.event('revision.upload.provided', user=user, **{
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user,
                            detail='uploaded requested revision')

    def add_revision_comment(self, user, revision, comment, reviewdocument):
        # toolkit/apps/matter/signals.py:103
        override_message = u'%s annotated %s in %s' % (user, revision.slug, revision.item)
        self._create_activity(actor=user, verb=u'added revision comment', action_object=revision,
                              override_message=override_message, comment=comment, item=revision.item,
                              reviewdocument=reviewdocument)
        self.analytics.event('revision.comment.added', user=user, **{
            'item_pk': revision.item.pk,
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=revision.item, ident=revision.item.slug, from_user=user,
                            detail='commented on revision')

    def add_review_copy_comment(self, user, revision, comment, reviewdocument):
        # toolkit/apps/matter/signals.py:103
        override_message = u'%s annotated %s (review comment) in %s' % (user, revision.slug, revision.item)
        self._create_activity(actor=user, verb=u'added review-session comment', action_object=revision,
                              override_message=override_message, comment=comment, item=revision.item,
                              reviewdocument=reviewdocument)
        self.analytics.event('revision.comment.added', user=user, **{
            'item_pk': revision.item.pk,
            'matter_pk': revision.item.matter.pk
        })

    def delete_revision_comment(self, user, revision):
        # toolkit/apps/matter/signals.py:103
        override_message = u'%s deleted a comment on %s' % (user, revision)
        self._create_activity(actor=user, verb=u'deleted revision comment', action_object=revision,
                              override_message=override_message, item=revision.item)
        self.realtime_event(event='update', obj=revision.item, ident=revision.item.slug, from_user=user,
                            detail='deleted revision comment')

    def revision_changed_status(self, user, revision, previous_status):
        # never used
        current_status = revision.display_status
        override_message = u"%s changed %s %s's status to %s" % (user, revision.item, revision.slug, current_status)
        self._create_activity(actor=user, verb=u'changed the status', action_object=revision, item=revision.item,
                              override_message=override_message, current_status=current_status,
                              previous_status=previous_status)
        self.realtime_event(event='update', obj=revision.item, ident=revision.item.slug, from_user=user,
                            detail='revision status changed')

    #
    # Attachments
    #

    def created_attachment(self, user, item, attachment):
        override_message = u'%s added an attachment to %s' % (user, item)
        self._create_activity(actor=user, verb=u'created', action_object=attachment, item=item,
                              override_message=override_message, filename=attachment.name,
                              date_created=attachment.date_created)

        self.analytics.event('attachment.create', user=user, **{
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='created attachment')

    def deleted_attachment(self, user, item, attachment):
        override_message = u'%s destroyed an attachment for %s' % (user, item)
        self._create_activity(actor=user, verb=u'deleted', action_object=attachment, item=item,
                              override_message=override_message, filename=attachment.name,
                              date_created=attachment.date_created)
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='deleted attachment')

    #
    # Review requests
    #
    def invite_user_as_reviewer(self, item, inviting_user, invited_user):
        # toolkit.api.views.review.ItemRevisionReviewersView#create
        if inviting_user.pk != invited_user:
            override_message = u'%s invited %s to review %s of %s' % (inviting_user, invited_user, item.latest_revision,
                                                                      item)
            self._create_activity(actor=inviting_user, verb=u'invited reviewer', action_object=item,
                                  override_message=override_message, user=invited_user)
            self.analytics.event('review.request.sent', user=inviting_user, **{
                'invited': invited_user.get_full_name(),
                'invited_type': invited_user.profile.type,
                'item_pk': item.pk,
                'matter_pk': self.matter.pk
            })
            self.realtime_event(event='update', obj=item, ident=item.slug, from_user=inviting_user,
                                detail='invited reviewer')

    def user_viewed_revision(self, item, user, revision):
        # toolkit.api.views.review.ReviewerHasViewedRevision#update
        override_message = u'%s viewed %s (%s) of %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'viewed revision', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.request.viewed', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })

    def user_downloaded_revision(self, item, user, revision):
        # toolkit.apps.review.views.DownloadRevision#render_to_response
        override_message = u'%s downloaded %s (%s) of %s' % (user, revision.name, revision.slug, item)
        self._create_activity(actor=user, verb=u'downloaded revision', action_object=revision,
                              override_message=override_message, item=item, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.request.comment.added', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })

    def user_revision_cancel(self, item, user, revision):
        override_message = u'%s canceled the revision of %s' % (user, revision)
        self._create_activity(actor=user, verb=u'cancelled review', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.request.cancelled', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user,
                            detail='user completed review of revision')

    def user_revision_review_complete(self, item, user, revision):
        # toolkit.apps.review.views.ApproveRevisionView#approve
        override_message = u'%s completed their review of %s' % (user, revision)
        self._create_activity(actor=user, verb=u'completed review', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.request.completed', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user,
                            detail='user completed review of revision')

    def all_revision_reviews_complete(self, item, revision):
        # toolkit.core.item.mixins.ReviewInProgressMixin#recalculate_review_percentage_complete
        override_message = u'All of the reviews of %s have been completed' % (item,)
        self._create_activity(actor=self.matter.lawyer, verb=u'completed all reviews', action_object=item,
                              override_message=override_message, revision=revision, filename=revision.name,
                              version=revision.slug, date_created=datetime.datetime.utcnow())
        self.analytics.event('review.all_requests.completed', user=self.matter.lawyer, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=None,
                            detail='revision review completed')

    #
    # Signing
    #
    def sent_setup_for_signing(self, user, sign_object):
        """
        HelloSign claim_url event
        """
        # toolkit.apps.sign.views#ClaimSignRevisionView.post
        revision = sign_object.document
        item = revision.item
        message = u'%s sent %s (%s) for signing' % (user, item, revision)
        self._create_activity(actor=user, verb=u'sent for signing', action_object=item, message=message,
                              user=user)
        self.analytics.event('sign.sent_doc_for_signing', user=user, **{
            'sign_object': str(sign_object.slug),
            'revision_pk': str(item.slug),
            'item_pk': item.pk,
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user,
                            detail='revision sent for signing')

    def completed_setup_for_signing(self, user, sign_object):
        """
        Completed the HelloSign claim_url event
        """
        # toolkit.apps.sign.views#ClaimSignRevisionView.post
        revision = sign_object.document
        item = revision.item
        message = u'%s completed signing setup %s (%s) for signing' % (user, item, revision)
        self._create_activity(actor=user, verb=u'completed signing setup', action_object=item, message=message,
                              user=user)
        self.analytics.event('sign.completed_signing_setup', user=user, **{
            'sign_object': str(sign_object.slug),
            'revision_pk': str(item.slug),
            'item_pk': item.pk,
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='signing setup completed')

    def invite_user_as_signer(self, item, inviting_user, invited_user):
        # toolkit.apps.sign.views#ClaimSignRevisionView.post
        message = u'%s invited %s as signer for %s' % (inviting_user, invited_user, item)
        self._create_activity(actor=inviting_user, verb=u'invited signer', action_object=item, message=message,
                              user=invited_user)
        self.analytics.event('sign.request.sent', user=inviting_user, **{
            'invited': invited_user.get_full_name(),
            'invited_type': invited_user.profile.type,
            'item_pk': item.pk,
            'matter_pk': self.matter.pk
        })

    def user_viewed_signature_request(self, user, signer, sign_document):
        # toolkit.apps.sign.views
        revision = sign_document.document
        item = revision.item

        message = u'%s viewed signature request %s for %s on item %s' % (user, revision.name, signer, item)
        self._create_activity(actor=user, verb=u'viewed signature request', action_object=item, message=message,
                              revision=revision, filename=revision.name, version=revision.slug,
                              date_created=datetime.datetime.utcnow())
        self.analytics.event('sign.request.viewed', user=user, **{
            'item_pk': item.pk,
            'matter_pk': self.matter.pk,
            'revision_pk': revision.pk
        })

    def user_signed(self, user, sign_object):
        # toolkit.apps.sign.signals
        revision = sign_object.document
        item = revision.item
        message = u'%s signed %s (%s)' % (user, item, revision)
        self._create_activity(actor=user, verb=u'signed', action_object=item, message=message,
                              user=user)
        self.analytics.event('sign.user_signed', user=user, **{
            'sign_object': str(sign_object.slug),
            'revision_pk': str(item.slug),
            'item_pk': item.pk,
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=user, detail='user signed revision')

    def all_users_have_signed(self, sign_object):
        # toolkit.apps.sign.signals
        revision = sign_object.document
        item = revision.item
        message = u'Signing Complete - All invitees have signed %s (%s)' % (item, revision)
        self._create_activity(actor=self.matter.lawyer, verb=u'signing complete', action_object=item, message=message,
                              user=self.matter.lawyer)
        self.analytics.event('sign.signing_complete', user=self.matter.lawyer, **{
            'sign_object': str(sign_object.slug),
            'revision_pk': str(item.slug),
            'item_pk': item.pk,
            'matter_pk': self.matter.pk
        })
        self.realtime_event(event='update', obj=item, ident=item.slug, from_user=None, detail='signing completed')
