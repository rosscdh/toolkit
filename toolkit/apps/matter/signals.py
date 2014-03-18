# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.dispatch import Signal, receiver

import dj_crocodoc.signals as crocodoc_signals

from toolkit.apps.workspace.models import InviteKey
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.core.signals import send_activity_log
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



@receiver(crocodoc_signals.crocodoc_comment_create)
@receiver(crocodoc_signals.crocodoc_comment_delete)
@receiver(crocodoc_signals.crocodoc_annotation_highlight)
@receiver(crocodoc_signals.crocodoc_annotation_strikeout)
@receiver(crocodoc_signals.crocodoc_annotation_textbox)
@receiver(crocodoc_signals.crocodoc_annotation_drawing)
# @receiver(crocodoc_signals.crocodoc_annotation_point)  # dont record this event because its pretty useless and comes by default when they comment
def crocodoc_webhook_event_recieved(sender, verb, document, target, attachment_name, user_info, crocodoc_event, **kwargs):
    """
    signal to handle any of the crocdoc signals
    """
    user_pk, user_full_name = user_info
    # @TODO cehck this user still exists
    user = User.objects.get(pk=user_pk)

    send_activity_log.send(user, **{
        'actor': user,
        'verb': verb,
        'action_object': target.item,
        'target': target.item.matter,
        'message': verb
    })