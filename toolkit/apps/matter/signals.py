# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.models import User
from django.dispatch import Signal, receiver
from django.db.models.signals import m2m_changed

import dj_crocodoc.signals as crocodoc_signals
from toolkit.apps.review.models import ReviewDocument

from toolkit.apps.workspace.models import Workspace

from toolkit.apps.workspace.models import InviteKey
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from .mailers import ParticipantAddedEmail


logger = logging.getLogger('django.request')


PARTICIPANT_ADDED = Signal(providing_args=['matter', 'participant', 'user', 'note'])


@receiver(PARTICIPANT_ADDED)
def participant_added(sender, matter, participant, user, note, **kwargs):
    next_url = matter.get_absolute_url()

    #
    # Create the invite key (it may already exist)
    #
    invite, is_new = InviteKey.objects.get_or_create(matter=matter,
                                                     invited_user=participant,
                                                     next=next_url)
    invite.inviting_user = user
    invite.save(update_fields=['inviting_user'])

    #
    # Send invite email
    #
    recipient = (participant.get_full_name(), participant.email)
    from_tuple = (user.get_full_name(), user.email)

    mailer = ParticipantAddedEmail(from_tuple=from_tuple, recipients=(recipient,))
    mailer.process(matter=matter,
                   user=user,
                   custom_message=note,
                   # use the Invites absolute url as the action url
                   # so we force them to enter passwords etc
                   action_url=ABSOLUTE_BASE_URL(invite.get_absolute_url()))

    matter.actions.added_matter_participant(matter=matter, adding_user=user, added_user=participant)


@receiver(m2m_changed, sender=Workspace.participants.through, dispatch_uid='matter.on_participant_added')
def on_participant_added(sender, instance, action, model, pk_set, **kwargs):
    """
    When we add a participant; ensure that they are also participants on all of the existing items
    @BUSINESSRULE
    @DB
    @VERYIMPORTANT
    """
    if action in ['post_add']:
        # loop over matter items
        # add user to the participants for that instance
        matter = instance
        for item in matter.item_set.all():
            for revision in item.revision_set.all():
                for reviewdocument in revision.reviewdocument_set.all():
                    #
                    ## issue a save which will cause the participants to be readded
                    #
                    # @TODO this is REALLY HEAVY
                    #
                    reviewdocument.save()


@receiver(crocodoc_signals.crocodoc_comment_create)
@receiver(crocodoc_signals.crocodoc_comment_update)  # reply to
@receiver(crocodoc_signals.crocodoc_comment_delete)
#@receiver(crocodoc_signals.crocodoc_annotation_highlight)
#@receiver(crocodoc_signals.crocodoc_annotation_strikeout)
@receiver(crocodoc_signals.crocodoc_annotation_textbox)
#@receiver(crocodoc_signals.crocodoc_annotation_drawing)
## @receiver(crocodoc_signals.crocodoc_annotation_point)  # dont record this event because its pretty useless and comes by default when they comment
def crocodoc_webhook_event_recieved(sender, verb, document, target, attachment_name, user_info, crocodoc_event,
                                    content=None, **kwargs):
    """
    signal to handle any of the crocdoc signals
    """
    matter = None

    user_pk, user_full_name = user_info

    try:
        user = User.objects.get(pk=user_pk)

    except User.DoesNotExist:
        pass

    else:
        # continue on we have a user
        #
        # are we looking at something that is a matter
        #
        if target.__class__.__name__ == 'Workspace':
            matter = target
        #
        # are we looking at something that has an item
        #
        if hasattr(target, 'item'):
            matter = target.item.matter

        if matter is not None:
            if crocodoc_event in ['annotation.create', 'comment.create', 'comment.update']:
                # user MUST be in document.source_object.primary_reviewdocument.reviewers
                # otherwise he could not get to this point

                reviewdocument = None
                try:
                    reviewdocument = document.source_object.reviewdocument_set.get(
                        crocodoc_uuid=document.crocodoc_uuid.replace('-', ''))  # not found with '-' in uuid
                except ReviewDocument.DoesNotExist:
                    logger.error(u'ReviewDocument not found for crocodoc_uuid (no comment saved): %s' % document.crocodoc_uuid)

                if reviewdocument:
                    if reviewdocument == document.source_object.primary_reviewdocument:
                        # this reviewdocument is the PRIMARY one, meaning: one that is not being externally reviewed
                        matter.actions.add_revision_comment(user=user, revision=document.source_object, comment=content)
                    else:
                        # otherwise it is externally reviewed -> add "(review copy)" to the displayed event
                        matter.actions.add_review_copy_comment(user=user, revision=document.source_object, comment=content)

            if crocodoc_event in ['annotation.delete', 'comment.delete']:
                matter.actions.delete_revision_comment(user=user, revision=document.source_object)
