# -*- coding: utf-8 -*-

from toolkit.mailers import BaseMailerService


class EightyThreeBCreatedEmail(BaseMailerService):
    """
    m = EightyThreeBCreatedEmail(
            subject='A new 83b has been created for you',
            message='{from_name} has created an 83b form for you, you can find it at {location}',
            from_tuple=('Ross', 'ross@lawpal.com'),
            recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'eightythreeb_created'


class EightyThreeBReminderEmail(BaseMailerService):
    """
    m = EightyThreeBReminderEmail(from_tuple=('Ross', 'ross@lawpal.com'),
                                  recipients=(('Alex', 'alex@lawpal.com')))
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


class EightyThreeMailDeliveredEmail(BaseMailerService):
    """
    m = EightyThreeMailDeliveredEmail(from_tuple=('Ross', 'ross@lawpal.com'),
                                      recipients=(('Alex', 'alex@lawpal.com')))
    m.process(company=instance.workspace,
              url='',
              current_status='',
              next_step='',
              current_step='',
              total_steps='',
              num_days_left='',
              percent_complete='',
              instance='')
    """
    email_template = 'eightythreeb_delivered'
