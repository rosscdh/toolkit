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
