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
    while _user_exists(username=username):
        LOGGER.info('Username %s exists, trying to create another' % username)
        username = '%s-%s' % (username, uuid.uuid4().get_hex()[:4])
        username = username[:30]

    return slugify(username)


def _get_or_create_user_profile(user):
    # set the profile
    # This is what triggers the whole cleint profile creation process in pipeline.py:ensure_user_setup
    profile, is_new = UserProfile.objects.get_or_create(user=user)  # added like this so django noobs can see the result of get_or_create
    return (profile, is_new,)

# used to trigger profile creation by accidental refernce. Rather use the _create_user_profile def above
User.profile = property(lambda u: _get_or_create_user_profile(user=u)[0])
