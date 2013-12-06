# -*- coding: utf-8 -*-
from django.db import models

from jsonfield import JSONField


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
