# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from .models import UserProfile

import uuid
import logging
LOGGER = logging.getLogger('django.request')


def _user_exists(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def _get_unique_username(username):
    username = slugify(username)  # apply the transforms first so that the lookup acts on the actual username
    while _user_exists(username=username):
        LOGGER.info('Username %s exists, trying to create another' % username)
        username = '%s-%s' % (username, uuid.uuid4().get_hex()[:4])
        username = username[0:30]

    return username
