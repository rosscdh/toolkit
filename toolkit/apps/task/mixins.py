# -*- coding: utf-8 -*-
from .mailers import TaskReminderEmail

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL


class SendReminderEmailMixin(object):
    def send_assigned_to_email(self, from_user, **kwargs):
        subject = '[ACTION REQUIRED] A task has been assigned to you'
        self.send_reminder(from_user=from_user, subject=subject, **kwargs)
        #
        # Set the marker that we have sent this email
        #
        self.data['send_assigned_to_email'] = True
        self.save(update_fields=['data'])

    def send_reminder(self, from_user, subject=None, **kwargs):
        # nto already completed
        if self.is_complete is False:

            for user in self.assigned_to.all():
                # send the invite url
                action_url = ABSOLUTE_BASE_URL(self.get_absolute_url())

                mailer = TaskReminderEmail(recipients=((user.get_full_name(), user.email,),),
                                           from_tuple=(from_user.get_full_name(), from_user.email,))
                mailer.process(item=self.item,
                               matter=self.item.matter,
                               from_name=from_user.get_full_name(),
                               action_url=action_url,  # please understsand the diff between action_url and next_url
                               description=self.description,
                               date_due=self.date_due,
                               **kwargs)
