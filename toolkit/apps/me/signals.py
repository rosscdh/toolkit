# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from django.contrib.auth.models import User
from .mailers import WelcomeEmail

import logging
LOGGER = logging.getLogger('django.request')


def _model_slug_exists(model, slug):
    try:
        return model.objects.get(slug=slug)
    except model.DoesNotExist:
        return None


@receiver(post_save, sender=User, dispatch_uid='me.send_welcome_email')
def send_welcome_email(sender, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    is_new = kwargs.get('created')
    user = kwargs.get('instance')

    if is_new is True:
        name = user.get_full_name() if user.get_full_name() is not None else ''
        mailer_service = WelcomeEmail(recipients=((name, user.email),))
        mailer_service.process()