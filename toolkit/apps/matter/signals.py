# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver
from django.db.models.signals import m2m_changed

from toolkit.apps.workspace.models import (Workspace,
                                           InviteKey,)
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from .mailers import ParticipantAddedEmail


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

