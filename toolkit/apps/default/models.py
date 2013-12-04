# -*- coding: utf-8 -*-
from django.db import models

from uuidfield import UUIDField
from jsonfield import JSONField


class InviteKey(models.Model):
    """
    Invite Key that allows a user to be invited to one or more projects
    """
    key = UUIDField(auto=True, db_index=True)
    user = models.ForeignKey('auth.User')
    tool = models.ForeignKey('workspace.Tool')
    next = models.CharField(max_length=255)  # user will be redirected here on login
    data = JSONField(default={})  # for any extra data that needs to be stored
    has_been_used = models.BooleanField(default=False)


class UserProfile(models.Model):
    """
    Base User Profile, where we store all the interesting information about
    users
    """
    user = models.OneToOneField('auth.User',
                                unique=True,
                                related_name='profile')

    data = JSONField(default={})

    @classmethod
    def create(cls, **kwargs):
        profile = cls(**kwargs)
        profile.save()
        return profile

    def __getattr__(self, key):
        try:
            # if key is of invalid type or value, the list values 
            # will raise the error
            return self.data[key]
        except KeyError:
            raise AttributeError

    def __unicode__(self):
        return '%s <%s>' % (self.user.get_full_name(), self.user.email)

    @property
    def user_class(self):
        return self.data.get('user_class', None)

    @property
    def is_lawyer(self):
        return self.user_class == 'lawyer'

    @property
    def is_customer(self):
        return self.user_class == 'customer'
