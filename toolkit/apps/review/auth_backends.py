# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, check_password

from .models import ReviewDocument

import logging
logger = logging.getLogger('django.request')


class ReviewDocumentBackend(object):
    """
    Authenticated based on the url
    /review/:slug/:unique_key
    where the slug gets the ReviewDocument
    and the :unique_key provides a lookup in the ReviewDocument.data['auth']
    which will provide the user pk
    """
    def authenticate(self, username=None, password=None):
        # Check the username/password and return a User.
        user = None
        try:

            review = ReviewDocument.objects.get(slug=username)
            pk = review.get_auth(auth_key=password)
            if pk is None:
                logger.error('ReviewDocument not found for: %s %s' % (review, password,))
                raise ObjectDoesNotExist

            user = User.objects.get(pk=pk)

        except Exception as e:
            logger.error('ReviewDocument.auth does not exist: %s reason: %s' % (username, e))

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None