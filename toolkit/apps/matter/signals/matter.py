# -*- coding: utf-8 -*-
import logging
from django.dispatch import Signal, receiver
from django.db.models.signals import (m2m_changed,
                                      post_save,
                                      post_delete)

from toolkit.apps.workspace.models import InviteKey
from toolkit.api.serializers import LiteUserSerializer
from toolkit.apps.workspace.models import Workspace, WorkspaceParticipants

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.apps.matter.mailers import ParticipantAddedEmail


logger = logging.getLogger('django.request')


PARTICIPANT_ADDED = Signal(providing_args=['matter', 'participant', 'user', 'note'])
PARTICIPANT_DELETED = Signal(providing_args=['matter', 'participant', 'user', 'note'])
USER_STOPPED_PARTICIPATING = Signal(providing_args=['matter', 'participant'])
USER_DOWNLOADED_EXPORTED_MATTER = Signal(providing_args=['matter', 'user'])


def _update_matter_participants(matter):
    """
    Participants optimisations; so we dont have millions of queries on matter_list
    and else where
    """
    participants_data = {'participants': []} # @BUSINESSRULE reset the participants list

    for u in matter.participants.all():
        participants_data.get('participants').append(LiteUserSerializer(u, context={'matter': matter}).data)

    matter.data.update(participants_data)

    matter.save(update_fields=['data'])


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

    if user != participant:
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

        matter.actions.added_matter_participant(adding_user=user, added_user=participant)


@receiver(PARTICIPANT_DELETED)
def participant_deleted(sender, matter, participant, user, **kwargs):
    matter.actions.removed_matter_participant(removing_user=user, removed_user=participant)


@receiver(USER_STOPPED_PARTICIPATING)
def user_stopped_participating(sender, matter, participant, **kwargs):
    matter.actions.user_stopped_participating(user=participant)


@receiver(USER_DOWNLOADED_EXPORTED_MATTER)
def user_downloaded_exported_matter(sender, matter, user, **kwargs):
    matter.actions.user_downloaded_exported_matter(user=user)


@receiver(post_save, sender=WorkspaceParticipants, dispatch_uid='review.post_save.update_matter_participants_cache')
def post_save_update_matter_participants_cache(sender, instance, **kwargs):
    _update_matter_participants(matter=instance.workspace)


@receiver(post_delete, sender=WorkspaceParticipants, dispatch_uid='review.post_delete.update_matter_participants_cache')
def post_delete_update_matter_participants_cache(sender, instance, **kwargs):
    _update_matter_participants(matter=instance.workspace)


@receiver(m2m_changed, sender=Workspace.participants.through, dispatch_uid='matter.on_participant_added')
def on_participant_added(sender, instance, action, model, pk_set, **kwargs):
    """
    When we add a participant; ensure that they are also participants on all of the existing items
    @BUSINESSRULE
    @DB
    @VERYIMPORTANT
    """
    matter = instance

    _update_matter_participants(matter=instance)

    if action in ['post_add']:
        # loop over matter items
        # add user to the participants for that instance
        for item in matter.item_set.all():
            for revision in item.revision_set.all():
                for reviewdocument in revision.reviewdocument_set.all():
                    #
                    ## issue a save which will cause the participants to be readded
                    #
                    # @TODO this is REALLY HEAVY
                    #
                    reviewdocument.save()


