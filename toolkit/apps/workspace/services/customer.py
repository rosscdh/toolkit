# -*- coding: utf-8 -*-
"""
Generic Customer services
"""
from django.contrib.auth.models import User

from toolkit.apps.default import _get_unique_username

from . import logger


class EnsureCustomerService(object):
    """
    Service to get or create a Customer User
    """
    def __init__(self, email, full_name=None):
        self.email = email
        self.full_name = full_name
        self.is_new, self.user, self.profile = (None, None, None)

    def process(self):
        if self.email is None:
            logger.error('Email is None, cant create user')
        else:
            self.is_new, self.user, self.profile = self.get_user(email=self.email)

    def get_user(self, email, **kwargs):

        try:
            user = User.objects.get(email=email, **kwargs)
            is_new = False

        except User.DoesNotExist:
            username = _get_unique_username(username=email.split('@')[0])
            user = User.objects.create(username=username,
                                       email=email,
                                       **kwargs)
            is_new = True

        profile = user.profile

        if is_new is True or 'user_class' not in profile.data:
            logger.info('Is a new User')
            profile.data['user_class'] = 'customer'
            profile.save(update_fields=['data'])

        # setup the name of the user
        # and set it if they exist but have no name
        if self.full_name is not None:
            logger.info('Full Name was provided')
            # extract the first and last name
            names = self.full_name.split(' ')
            update_fields = []

            if user.first_name in [None, '']:
                user.first_name = names[0]
                update_fields.append('first_name')
                logger.info('Updating first_name')

            if user.last_name in [None, '']:
                user.last_name = ' '.join(names[1:])
                update_fields.append('last_name')
                logger.info('Updating last_name')

            # save the user model
            user.save(update_fields=update_fields)

        return is_new, user, profile
