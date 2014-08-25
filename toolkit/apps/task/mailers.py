# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage



class TaskReminderEmail(BaseMailerService):
    """
    m = TaskReminderEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'task_reminder'

    def __init__(self, task, **kwargs):
        self.task = task
        super(TaskReminderEmail, self).__init__(**kwargs)

    @property
    def subject(self):
        return '[ACTION REQUIRED] (Expired) Please complete the task' if self.task.has_expired else '[ACTION REQUIRED] Please complete the task'

    @subject.setter
    def subject(self, value):
        """
        do nothing
        """
        pass