# -*- coding: utf-8 -*-
from django.conf import settings
from toolkit.mailers import BaseMailerService, BaseSpecifiedFromMailerService
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class EightyThreeBCreatedEmail(BaseSpecifiedFromMailerService):
    """
    m = EightyThreeBCreatedEmail(
            from_tuple=('Ross', 'ross@lawpal.com'), 
            subject='A new 83b has been created for you',
            message='{from_name} has created an 83b form for you, you can find it at {location}',
            recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'eightythreeb_created'



class EightyThreeBReminderEmail(BaseSpecifiedFromMailerService):
    """
    m = EightyThreeBReminderEmail(from_tuple=('Ross', 'ross@lawpal.com'), recipients=(('Alex', 'alex@lawpal.com')))
    m.process(company='',
              url='https://lawpal.com/workspace/lawpal-internal-d570/tool/83b-election-letters/c1b7d38cf90a4c158ae8e7b810d4c7f6/preview/',
              current_status='Description of the current step',
              next_step='Description of the next step',
              current_step=2,
              total_steps=4,
              num_days_left=3,
              instance=instance_of_83b)
    """
    email_template = 'eightythreeb_reminder'



class EightyThreeTrackingCodeEnteredEmail(BaseMailerService):
    """
    Send an email to all participants with the attachments

    m = EightyThreeMailDeliveredEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process(instance=:instance)
    """
    email_template = 'eightythreeb_trackingcode_attached'

    def process(self, **kwargs):
        """
        This override will download the attachments and send them to the email as
        attachments; @TODO make this an async task
        """
        instance = kwargs.get('instance')

        attachments = []
        for a in instance.attachment_set.all():
            path = default_storage.save(a.attachment.name, ContentFile(a.attachment.read()))
            attachments.append('%s/%s' % (settings.MEDIA_ROOT, path,))  # append the name path to list

        super(EightyThreeTrackingCodeEnteredEmail, self).process(attachments=attachments,
                                                                 **kwargs)



class EightyThreeMailDeliveredEmail(BaseSpecifiedFromMailerService):
    """
    m = EightyThreeMailDeliveredEmail(from_tuple=('Ross', 'ross@lawpal.com'), recipients=(('Alex', 'alex@lawpal.com')))
    m.process(instance='')
    """
    email_template = 'eightythreeb_delivered'
