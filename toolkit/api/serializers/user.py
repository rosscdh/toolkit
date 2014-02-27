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
    initials = serializers.SerializerMethodField('get_initials')
    user_class = serializers.SerializerMethodField('get_user_class')

    class Meta:
        model = User
        lookup_field = 'username'
        fields = ('url', 'first_name', 'last_name', 'initials', 'user_class')

    def get_initials(self, obj):
        return obj.get_initials()

    def get_user_class(self, obj):
        return obj.profile.user_class
