# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework import serializers

from toolkit.apps.default.models import UserProfile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    #account = serializers.HyperlinkedRelatedField(source='profile', many=False, view_name='account-detail', lookup_field='username')

    class Meta:
        model = User
        lookup_field = 'username'
        fields = ('url', 'username', 'first_name',
                  'last_name', 'email', 'is_active',)