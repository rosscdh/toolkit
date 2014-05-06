# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

import base64
import hashlib
import logging
logger = logging.getLogger('django.request')


class UserAuthMixin(object):
    """
    On the addition of a reviewer create a new auth object
    that consists of {
        "reviewer.pk": ":random_slug_for_url"
    }
    this is then used in the auth_backends.ReviewDocumentBackend

    On the removal of a reviewer remove the auth object
    that consists of {
        "reviewer.pk": ":random_slug_for_url"
    }
    this is then used in the auth_backends.ReviewDocumentBackend
    """

    @property
    def auth(self):
        return self.data.get('auth', {})

    @auth.setter
    def auth(self, value):
        if type(value) in [dict]:
            self.data['auth'] = value
        else:
            raise Exception('.auth must be a dict')

    def get_auth(self, auth_key):
        """
        Provide the User.pk based on an auth_slug key passed in
        """
        if auth_key in self.auth.values():  # .values is the list of auth_keys
            for user_pk, present_auth_key in self.auth.iteritems():
                if auth_key == present_auth_key:
                    return int(user_pk)  # Msut return int
        return None

    def get_user_auth(self, user):
        """
        Provide the auth key for the user
        """
        user_pk = str(user.pk)
        if user_pk in self.auth.keys():
            try:
                return [auth for key_pk, auth in self.auth.iteritems() if key_pk == user_pk][0]
            except IndexError:
                pass
        return None

    def recompile_auth_keys(self):
        """
        When we clone the template review document we need to regenerate all of the
        keys for all of the participants
        @DANGER @BUSINESSRULE this will change all auth urls issued
        """
        for user_pk in self.auth.keys():
            user = User.objects.get(pk=user_pk)
            self.authorise_user_access(user=user)

    def make_user_auth_key(self, user):
        """
        do not enforce access for the user here to allow testing
        """
        hasher = hashlib.sha1('%s-%s' % (str(self.slug), user.email))
        return base64.urlsafe_b64encode(hasher.digest()[0:10])

    def authorise_user_access(self, user):
        """
        @BUSINESSRULE make sure the user only gets one key per review
        """
        auth = self.auth

        if user and str(user.pk) not in auth.keys():
            # generate a key
            key = self.make_user_auth_key(user=user)
            # set the auth
            auth.update({str(user.pk): key})
            # update the model
            self.auth = auth

    def deauthorise_user_access(self, user):
        auth = self.auth

        if user and str(user.pk) in auth.keys():

            for user_pk, key in auth.iteritems():
                if int(user_pk) == int(user.pk):
                    del auth[user_pk]
                    break
            self.auth = auth
            self.save(update_fields=['data'])
