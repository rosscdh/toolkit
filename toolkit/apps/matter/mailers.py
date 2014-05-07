from toolkit.mailers import BaseSpecifiedFromMailerService, BaseMailerService


class ParticipantAddedEmail(BaseSpecifiedFromMailerService):
    email_template = 'participant_added'


class MatterExportFinishedEmail(BaseMailerService):
    """
    m = MatterExportFinishedEmail(
            subject='The export has finished',
            message='{from_name} has created an 83b form for you, you can find it at {location}',
            recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'matter_export_finished'