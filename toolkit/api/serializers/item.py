# -*- coding: UTF-8 -*-
"""
Items are either todo items or document items
"""
from django.contrib.auth.models import User
from rest_framework import serializers

from toolkit.core.item.models import Item

from user import UserSerializer
from . import HATOAS

import datetime
import random

USERS = User.objects.all()

class ItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    item_type = serializers.SerializerMethodField('get_item_type')
    date_due = serializers.SerializerMethodField('get_date_due')
    revisions = serializers.SerializerMethodField('get_revisions')
    participants = serializers.SerializerMethodField('get_participants')
    reviewers = serializers.SerializerMethodField('get_reviewers')
    signatories = serializers.SerializerMethodField('get_signatories')
    state = serializers.SerializerMethodField('get_state')
    is_complete = serializers.SerializerMethodField('get_is_complete')

    date_created = serializers.SerializerMethodField('get_date_created')
    date_modified = serializers.SerializerMethodField('get_date_modified')

    class Meta:
        model = Item
        exclude = ('name', 'workspace', 'item_type', 'revisions',
                   'participants', 'reviewers', 'signatories', 'is_complete',
                   'data', 'date_due', 'date_created', 'date_modified',)

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
            'url': '/api/v1/attachments/:slug/:revision',
            'revision': 1,
            'is_completed': False,
            'is_reviewed': False,
            'is_signed': False
        }
        revisions = []
        for i in xrange(0,3):
            item = doc.copy()
            item.update({'revision': i})
            revisions.append(item)
        revisions.reverse() # latest first
        result = HATOAS.copy()
        result.update({'url': '/api/v1/matter/:slug/items/:slug/revisions/', 'results': revisions[0]})
        return result

    def get_participants(self, obj):
        """
        placeholder
        '/api/v1/users/:pk'
        """
        result = HATOAS.copy()
        results = [UserSerializer(u).data.get('url') for u in random.choice([[], USERS[0:3]]) if u is not None]
        result.update({'url': '/api/v1/matter/:slug/items/:slug/participants/', 'results': results})
        return result

    def get_reviewers(self, obj):
        """
        placeholder
        """
        result = HATOAS.copy()
        results = [UserSerializer(u).data.get('url') for u in random.choice([[], USERS[1:2]]) if u is not None]
        result.update({'url': '/api/v1/matter/:slug/items/:slug/reviewers/', 'results': results})
        return result

    def get_signatories(self, obj):
        """
        placeholder
        """
        result = HATOAS.copy()
        results = [UserSerializer(u).data.get('url') for u in random.choice([[], USERS[2:3]]) if u is not None]
        result.update({'url': '/api/v1/matter/:slug/items/:slug/signatories/', 'results': results})
        return result

    def get_state(self, obj):
        """
        placeholder
        @NOTE a set of workflow markers that may apply to the current
        """
        marker = {
            'url': '/api/v1/matter/:slug/items/:slug/states/:uuid/',
            'name': 'Signature',
            'slug': 'signature',
            'description': 'A Signature is required from Ross Customer',
            'status': 'Text Description of current step',
            'assignee': '/api/v1/rossc',
        }
        result = HATOAS.copy()
        results = [marker]
        result.update({'url': '/api/v1/matter/:slug/items/:slug/states/', 'results': results})
        return result

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

