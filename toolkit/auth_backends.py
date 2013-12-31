# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, check_password

from toolkit.apps.workspace.models import InviteKey

import logging
LOGGER = logging.getLogger('django.request')


class EmailBackend(object):
    def authenticate(self, username=None, password=None):
        # Check the username/password and return a User.
        user = None
        pwd_valid = False

        try:
            user = User.objects.get(email=username)
            pwd_valid = check_password(password, user.password)
        except User.DoesNotExist:
            LOGGER.error('User does not exist: %s' % username)

        if user and pwd_valid:
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class SecretKeyBackend(EmailBackend):
    def authenticate(self, username=None, password=None):
        # Check the username/password and return a User.
        user = None
        pwd_valid = False

        try:
            invite = InviteKey.objects.get(key=username)
            if invite.has_been_used is True:
                LOGGER.error('InviteKey has already been used: %s' % username)
                raise ObjectDoesNotExist

            user = invite.invited_user

        except ObjectDoesNotExist, InviteKey.DoesNotExist, DataError:
            LOGGER.error('InviteKey does not exist: %s' % username)

        return user
