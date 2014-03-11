from django.dispatch import Signal, receiver

from .mailers import ParticipantAddedEmail


PARTICIPANT_ADDED = Signal(providing_args=['matter', 'participant', 'user'])


@receiver(PARTICIPANT_ADDED)
def participant_added(sender, matter, participant, user, **kwargs):
    recipient = (participant.get_full_name(), participant.email)

    from_tuple = (user.get_full_name(), user.email)

    mailer = ParticipantAddedEmail(from_tuple=from_tuple, recipients=(recipient,))
    mailer.process(custom_message=False, matter=matter, user=user)
