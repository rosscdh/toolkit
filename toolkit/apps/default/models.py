# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from jsonfield import JSONField


class UserProfile(models.Model):
    """
    Base User Profile, where we store all the interesting information about
    users
    """
    user = models.OneToOneField('auth.User',
                                unique=True,
                                related_name='profile')

    data = JSONField(default={"user_class": "customer"})

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

    @property
    def type(self):
        return 'Attorney' if self.is_lawyer else 'Client'


def _get_or_create_user_profile(user):
    # set the profile
    # This is what triggers the whole cleint profile creation process in pipeline.py:ensure_user_setup
    profile, is_new = UserProfile.objects.get_or_create(user=user)  # added like this so django noobs can see the result of get_or_create
    return (profile, is_new,)

# used to trigger profile creation by accidental refernce. Rather use the _create_user_profile def above
User.profile = property(lambda u: _get_or_create_user_profile(user=u)[0])
