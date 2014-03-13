# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

import base64
import hashlib


class UserAuthMixin(object):
    """
    On the addition of a signer create a new auth object
    that consists of {
        ":random_slug_for_url": signer.pk
    }
    this is then used in the auth_backends.SignDocumentBackend

    On the removal of a signer remove the auth object
    that consists of {
        ":random_slug_for_url": signer.pk
    }
    this is then used in the auth_backends.SignDocumentBackend
    """

    @property
    def auth(self):
        return self.data.get('auth', {})

    @auth.setter
    def auth(self, value):
        if type(value) in [dict]:
            self.data['auth'] = value

    def get_auth(self, key):
        """
        Provide the User.pk based on an auth_slug key passed in
        """
        if key in self.auth.keys():
            return self.auth.get(key)
        return None

    def get_user_auth(self, user):
        """
        Provide the auth key for the user
        """
        if user.pk in self.auth.values():
            try:
                return [auth for auth, pk in self.auth.iteritems() if pk == user.pk][0]
            except IndexError:
                pass
        return None

    def recompile_auth_keys(self):
        """
        When we clone the template sign document we need to regenerate all of the
        keys for all of the participants
        @DANGER @BUSINESSRULE this will change all auth urls issued
        """
        for user_pk in self.auth.values():
            user = User.objects.get(pk=user_pk)
            self.authorise_user_to_sign(user=user)

    def make_user_auth_key(self, user):
        """
        do not enforce access for the user here to allow testing
        """
        hasher = hashlib.sha1('%s-%s' % (str(self.slug), user.email))
        return base64.urlsafe_b64encode(hasher.digest()[0:10])

    def authorise_user_to_sign(self, user):
        """
        @BUSINESSRULE make sure the user only gets one key per sign
        """
        auth = self.auth
        if user and user.pk not in auth.values():
            # generate a key
            key = self.make_user_auth_key(user=user)
            # set the auth
            auth.update({key: user.pk})
            # update the model
            self.auth = auth
            self.save(update_fields=['data'])

    def deauthorise_user_to_sign(self, user):
        auth = self.auth

        if user and user.pk in auth.values():

            for key, value in auth.iteritems():
                if value == user.pk:
                    del auth[key]
                    break
            self.auth = auth
            self.save(update_fields=['data'])
