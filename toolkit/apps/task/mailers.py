# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage



class TaskReminderEmail(BaseMailerService):
    """
    m = TaskReminderEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    subject = '[ACTION REQUIRED] Please complete this task that is assigned to you'
    email_template = 'task_reminder'
