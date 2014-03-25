# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, check_password

from .models import SignDocument

import logging
logger = logging.getLogger('django.request')


class SignDocumentBackend(object):
    """
    Authenticated based on the url
    /sign/:slug/:unique_key
    where the slug gets the SignDocument
    and the :unique_key provides a lookup in the SignDocument.data['auth']
    which will provide the user pk
    """
    def authenticate(self, username=None, password=None):
        # Check the username/password and return a User.
        user = None

        try:

            sign = SignDocument.objects.get(slug=username)
            pk = sign.get_auth(auth_key=password)
            if pk is None:
                logger.error('SignDocument not found for: %s %s' % (sign, password,))
                raise ObjectDoesNotExist

            user = User.objects.get(pk=pk)

        except Exception as e:
            logger.error('SignDocument.auth does not exist: %s reason: %s' % (username, e))

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None