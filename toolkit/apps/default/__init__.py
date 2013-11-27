# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from .models import UserProfile


def _get_or_create_user_profile(user):
    # set the profile
    # This is what triggers the whole cleint profile creation process in pipeline.py:ensure_user_setup
    profile, is_new = UserProfile.objects.get_or_create(user=user)  # added like this so django noobs can see the result of get_or_create
    return (profile, is_new,)

# used to trigger profile creation by accidental refernce. Rather use the _create_user_profile def above
User.profile = property(lambda u: _get_or_create_user_profile(user=u)[0])