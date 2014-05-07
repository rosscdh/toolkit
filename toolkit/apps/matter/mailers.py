from toolkit.mailers import BaseSpecifiedFromMailerService, BaseMailerService


class ParticipantAddedEmail(BaseSpecifiedFromMailerService):
    email_template = 'participant_added'


class MatterExportFinishedEmail(BaseMailerService):
    """
        m = MatterExportFinishedEmail(
            subject='Export has finished',
            message='Your matter "{{ matter.name }}" has been exported and is ready to be downloaded from: %s' % exported_matter.file.url,
            recipients=((matter.lawyer.get_full_name(), matter.lawyer.email)))
        m.process()
    """
    email_template = 'matter_export_finished'