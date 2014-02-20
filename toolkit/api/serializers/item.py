# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from django.contrib.auth.models import User
from rest_framework import serializers

from toolkit.core.item.models import Item

from .user import UserSerializer

from . import HATOAS

import datetime
import random

#USERS = User.objects.all()


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.SerializerMethodField('get_status')
    latest_revision = serializers.Field(source='latest_revision')

    closing_group = serializers.SerializerMethodField('get_closing_group')

    class Meta:
        model = Item
        lookup_field = 'slug'
        exclude = ('data', 'responsible_party')

    def get_status(self, obj):
        """
        placeholder
        open = new and pending
        final = ready for review+signing (may not actually happen tho)
        executed = approved and signed
        'one of open|awaiting document|final|executed'
        """
        return obj.display_status

    def get_participants(self, obj):
        """
        placeholder
        '/api/v1/users/:pk'
        @TODO is this necessary for items?
        """
        return []

    def get_reviewers(self, obj):
        """
        placeholder
        """
        if obj.latest_revision is not None:
            return obj.latest_revision.reviewers.all()
        return []

    def get_signatories(self, obj):
        """
        placeholder
        """
        if obj.latest_revision is not None:
            return obj.latest_revision.signatories.all()
        return []

    def get_closing_group(self, obj):
        """
        placeholder
        """
        return 'for finance'
