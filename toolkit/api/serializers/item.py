# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from django.contrib.auth.models import User
from rest_framework import serializers

#from toolkit.core.item.models import Item

from user import UserSerializer

import datetime
import random

USERS = User.objects.all()

#class ItemSerializer(serializers.ModelSerializer):
class ItemSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField('get_name')
    item_type = serializers.SerializerMethodField('get_item_type')
    date_due = serializers.SerializerMethodField('get_date_due')
    revisions = serializers.SerializerMethodField('get_revisions')
    participants = serializers.SerializerMethodField('get_participants')
    reviewers = serializers.SerializerMethodField('get_reviewers')
    signatories = serializers.SerializerMethodField('get_signatories')
    markers = serializers.SerializerMethodField('get_markers')
    is_complete = serializers.SerializerMethodField('get_is_complete')

    date_created = serializers.SerializerMethodField('get_date_created')
    date_modified = serializers.SerializerMethodField('get_date_modified')

    def get_name(self, obj):
        """
        placeholder
        """
        return 'Fixture Item: %s' % random.random()

    def get_item_type(self, obj):
        """
        placeholder
        @NOTE I dont feel this is necessary as all items have an attachment
        which has revisions and possibly could have reviewers and/or signatories
        so why seperate them. simply show the buttons on all and if they are
        used, then they are used if not then they are not used.
        """
        return 'One of (negotiated|upload_only)'

    def get_date_due(self, obj):
        """
        placeholder
        """
        return datetime.datetime.utcnow()

    def get_revisions(self, obj):
        """
        placeholder
        @NOTE orderd from most recent to oldest, but shown as the most recent
        is revision 3 in this case
        """
        doc = {
            'pk': '/url/to/attachment/:pk',
            'revision': 1,
            'is_reviewed': False,
            'is_signed': False
        }
        for i in xrange(0,3):
            doc.copy().update({'revision': i})
            yield doc

    def get_participants(self, obj):
        """
        placeholder
        """
        '/api/v1/users/:pk'
        return [UserSerializer(u).data.get('url') for u in random.choice([[], USERS[0:3]]) if u is not None]

    def get_reviewers(self, obj):
        """
        placeholder
        """
        return [UserSerializer(u).data.get('url') for u in random.choice([[], USERS[1:2]]) if u is not None]

    def get_signatories(self, obj):
        """
        placeholder
        """
        return [UserSerializer(u).data.get('url') for u in random.choice([[], USERS[2:3]]) if u is not None]

    def get_markers(self, obj):
        """
        placeholder
        @NOTE a set of workflow markers that may apply to the current
        """
        marker = {
            'name': 'Signature',
            'description': 'Description of the current task',
            'action': '/url/to/workflow/step',
            'status': 'Text Description of current step',
            'assignee': '/api/v1/rossc',
        }
        return [marker]

    def get_is_complete(self, obj):
        """
        placeholder
        """
        return random.choice([True,False])

    def get_date_created(self, obj):
        """
        placeholder
        """
        return datetime.datetime.utcnow()

    def get_date_modified(self, obj):
        """
        placeholder
        """
        return datetime.datetime.utcnow()

