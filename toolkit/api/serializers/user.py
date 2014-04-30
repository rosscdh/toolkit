# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from django.contrib.auth.models import User

from toolkit.apps.default.templatetags.intercom_tags import _get_intercom_user_hash

from rest_framework import serializers


def _get_user_review(self, obj, context):
    """
    Try to provide an initial reivew url from the base review_document obj
    for the currently logged in user
    """
    request = context.get('request')
    review_document = context.get('review_document', None)

    if request is not None:
        #
        # if we have a review_document present in the context
        #
        if review_document is None:
            # we have none, then try find the reviewdocument object that has all the matter participants in it
            #
            # The bast one will have 0 reviewers! and be the last in the set (because it was added first)
            #
            review_document = obj.reviewdocument_set.all().last()

        return review_document

    return None


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    The full representation of a User.
    """
    #account = serializers.HyperlinkedRelatedField(source='profile', many=False, view_name='account-detail', lookup_field='username')
    initials = serializers.SerializerMethodField('get_initials')
    name = serializers.SerializerMethodField('get_full_name')
    user_class = serializers.SerializerMethodField('get_user_class')
    intercom_user_hash = serializers.SerializerMethodField('get_intercom_user_hash')

    class Meta:
        model = User
        lookup_field = 'username'

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_initials(self, obj):
        return obj.get_initials()

    def get_user_class(self, obj):
        return obj.profile.user_class

    def get_intercom_user_hash(self, obj):
        return _get_intercom_user_hash(user_identifier=obj.username)


class LiteUserSerializer(UserSerializer):
    """
    The lite representation of a User.

    Used when a user is referenced in other API objects.
    """
    class Meta(UserSerializer.Meta):
        fields = ('url', 'username', 'name', 'initials', 'first_name', 'last_name', 'email', 'user_class',
                  'intercom_user_hash', 'date_joined')


class SimpleUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('url', 'username', 'name', 'initials', 'user_class')


class SimpleUserWithReviewUrlSerializer(SimpleUserSerializer):
    """
    User serilizer to provide a user object with the very important
    user_review_url
    """
    user_review = serializers.SerializerMethodField('get_user_review')

    class Meta(SimpleUserSerializer.Meta):
        fields = SimpleUserSerializer.Meta.fields +('user_review',)

    def get_user_review(self, obj):
        """
        Try to provide an initial reivew url from the base review_document obj
        """
        context = getattr(self, 'context', None)
        request = context.get('request')

        review_document = _get_user_review(self=self, obj=obj, context=context)

        if review_document is not None:
            return {
                'url': review_document.get_absolute_url(user=request.user),
                'slug': review_document.slug
            }

        return None
