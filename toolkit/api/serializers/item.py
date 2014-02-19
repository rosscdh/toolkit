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

USERS = User.objects.all()


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    #name = serializers.SerializerMethodField('get_name')
    #description = serializers.SerializerMethodField('get_description')

    #date_due = serializers.SerializerMethodField('get_date_due')
    #responsible_party = serializers.SerializerMethodField('get_responsible_party')
    status = serializers.SerializerMethodField('get_status')

    latest_revision = serializers.Field(source='latest_revision')

    participants = serializers.SerializerMethodField('get_participants')
    reviewers = serializers.SerializerMethodField('get_reviewers')
    signatories = serializers.SerializerMethodField('get_signatories')

    closing_group = serializers.SerializerMethodField('get_closing_group')

    #magic_powers = serializers.SerializerMethodField('get_magic_powers')

    class Meta:
        model = Item
        exclude = ('data',)

    # def get_name(self, obj):
    #     """
    #     placeholder
    #     """
    #     return 'Fixture Item: %s' % random.random()

    # def get_description(self, obj):
    #     """
    #     placeholder
    #     """
    #     return 'This is a small note about the Fixture Item: %s to give the client context' % random.random()

    # def get_date_due(self, obj):
    #     """
    #     placeholder
    #     """
    #     return datetime.datetime.utcnow()

    # def get_responsible_party(self, obj):
    #     """
    #     placeholder
    #     @NOTE affects how status is reflected; if we have a resparty and no file attached
    #     we are in "awaiting document" status
    #     """
    #     return None

    def get_status(self, obj):
        """
        placeholder
        open = new and pending
        final = ready for review+signing (may not actually happen tho)
        executed = approved and signed
        'one of open|awaiting document|final|executed'
        """
        return obj.display_status

    # def get_revisions(self, obj):
    #     """
    #     placeholder
    #     @NOTE orderd from most recent to oldest, but shown as the most recent
    #     is revision 3 in this case
    #     """
    #     doc = {
    #         'url': '/api/v1/attachments/:slug/:revision',
    #         'revision': 1,
    #         'is_completed': False,
    #         'is_reviewed': False,
    #         'is_signed': False
    #     }
    #     revisions = []
    #     for i in xrange(0,3):
    #         item = doc.copy()
    #         item.update({'revision': i})
    #         revisions.append(item)
    #     revisions.reverse() # latest first
    #     result = HATOAS.copy()
    #     result.update({'url': '/api/v1/matter/:slug/items/:slug/revisions/', 'results': revisions[0]})
    #     return result

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

    # def get_magic_powers(self, obj):
    #     """
    #     placeholder
    #     @NOTE a set of workflow markers that may apply to the current
    #     """
    #     marker = {
    #         'url': '/api/v1/matter/:slug/items/:slug/states/:uuid/',
    #         'name': 'Signature',
    #         'slug': 'signature',
    #         'description': 'A Signature is required from Ross Customer',
    #         'status': 'Text Description of current step',
    #         'assignee': '/api/v1/rossc',
    #     }
    #     result = HATOAS.copy()
    #     results = [marker]
    #     result.update({'url': '/api/v1/matter/:slug/items/:slug/states/', 'results': results})
    #     return result

    # def get_is_complete(self, obj):
    #     """
    #     placeholder
    #     """
    #     return random.choice([True,False])

    # def get_date_created(self, obj):
    #     """
    #     placeholder
    #     """
    #     return datetime.datetime.utcnow()

    # def get_date_modified(self, obj):
    #     """
    #     placeholder
    #     """
    #     return datetime.datetime.utcnow()

