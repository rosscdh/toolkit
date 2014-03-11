from toolkit.mailers import BaseSpecifiedFromMailerService


class ParticipantAddedEmail(BaseSpecifiedFromMailerService):
    email_template = 'participant_added'
