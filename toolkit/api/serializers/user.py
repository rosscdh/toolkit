# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework import serializers

from toolkit.apps.default.models import UserProfile


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        #exclude = ()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        lookup_field = 'username'
        fields = ('id', 'url', 'last_login', 'username', 'first_name',
                  'last_name', 'email', 'is_active', 'date_joined',)