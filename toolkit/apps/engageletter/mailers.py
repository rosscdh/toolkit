# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage



class EngageLetterLawyerSignEmail(BaseMailerService):
    """
    m = EngageLetterLawyerSignEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'engageletter_lawyer_sign'
