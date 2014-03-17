# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from django.contrib.auth.models import User

from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    The full representation of a User.
    """
    #account = serializers.HyperlinkedRelatedField(source='profile', many=False, view_name='account-detail', lookup_field='username')
    initials = serializers.SerializerMethodField('get_initials')
    name = serializers.SerializerMethodField('get_full_name')
    user_class = serializers.SerializerMethodField('get_user_class')

    class Meta:
        model = User
        lookup_field = 'username'

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_initials(self, obj):
        return obj.get_initials()

    def get_user_class(self, obj):
        return obj.profile.user_class


class LiteUserSerializer(UserSerializer):
    """
    The lite representation of a User.

    Used when a user is referenced in other API objects.
    """
    class Meta(UserSerializer.Meta):
        fields = ('url', 'username', 'name', 'initials', 'first_name', 'last_name', 'email', 'user_class')


class SimpleUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('url', 'name', 'initials', 'user_class')


class SimpleUserWithReviewUrlSerializer(SimpleUserSerializer):
    """
    User serilizer to provide a user object with the very important
    user_review_url
    """
    user_review_url = serializers.SerializerMethodField('get_user_review_url')

    class Meta(SimpleUserSerializer.Meta):
        fields = SimpleUserSerializer.Meta.fields +('user_review_url',)

    def get_user_review_url(self, obj):
        """
        Try to provide an initial reivew url from the base review_document obj
        """
        context = getattr(self, 'context', None)
        request = context.get('request')

        if request is not None:
            initial_reviewdocument = obj.reviewdocument_set.all().first()
            return initial_reviewdocument.get_absolute_url(user=request.user)

        return None