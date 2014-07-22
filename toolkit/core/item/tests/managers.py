# -*- coding: utf-8 -*-
from datetime import datetime
import uuid

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from model_mommy import mommy
from model_mommy.recipe import Recipe

from toolkit.casper.workflow_case import BaseScenarios

from ..managers import ItemManager
from ..models import Item


class ItemManagerTest(BaseScenarios, TestCase):
    def setUp(self):
        super(ItemManagerTest, self).setUp()
        self.basic_workspace()

        item = Recipe('item.Item', matter=self.matter)
        revision = Recipe('attachment.Revision')

        """
        Generic
        """
        # item, revisions: 0
        self.item1 = item.make()

        # item (completed), revisions: 0
        self.item2 = item.make(is_complete=True)

        # item, revisions: 0, responsible: user
        self.item3 = item.make(responsible_party=self.user)

        # item (completed), revisions: 0, responsible: user
        self.item4 = item.make(is_complete=True, responsible_party=self.user)

        # item, revisions: 0, responsible: other
        self.item5 = item.make(responsible_party=self.lawyer)

        # item (completed), revisions: 0, responsible: other
        self.item6 = item.make(is_complete=True, responsible_party=self.lawyer)

        """
        Requested
        """
        # item (requested), revisions: 0, responsible: user
        self.item7 = item.make(is_requested=True, responsible_party=self.user)

        # item (completed, requested), revisions: 0, responsible: user
        self.item8 = item.make(is_complete=True, is_requested=True, responsible_party=self.user)

        # item (requested), revisions: 0, responsible: other
        self.item9 = item.make(is_requested=True, responsible_party=self.lawyer)

        # item (completed, requested), revisions: 0, responsible: other
        self.item10 = item.make(is_complete=True, is_requested=True, responsible_party=self.lawyer)

        """
        Needs Review
        """
        # item (in review), revision: stale, reviewer: user
        self.item11 = item.make()
        self.item11revs = revision.make(item=self.item11, _quantity=2)
        self.item11revs[0].reviewers.add(self.user)

        # item (in review, completed), revision: stale, reviewer: user
        self.item12 = item.make(is_complete=True)
        self.item12revs = revision.make(item=self.item12, _quantity=2)
        self.item12revs[0].reviewers.add(self.user)

        # item (in review), revision: stale, reviewer: other
        self.item13 = item.make()
        self.item13revs = revision.make(item=self.item13, _quantity=2)
        self.item13revs[0].reviewers.add(self.lawyer)

        # item (in review, completed), revision: stale, reviewer: other
        self.item14 = item.make(is_complete=True)
        self.item14revs = revision.make(item=self.item14, _quantity=2)
        self.item14revs[0].reviewers.add(self.lawyer)

        # item (reviewed), revision: stale, reviewer: user
        self.item15 = item.make()
        self.item15revs = revision.make(item=self.item15, _quantity=2)
        self.item15revs[0].reviewers.add(self.user)
        self.item15revs[0].reviewdocument_set.filter(reviewers__in=[self.user]).update(is_complete=True)

        # item (reviewed, completed), revision: stale, reviewer: user
        self.item16 = item.make(is_complete=True)
        self.item16revs = revision.make(item=self.item16, _quantity=2)
        self.item16revs[0].reviewers.add(self.user)
        self.item16revs[0].reviewdocument_set.filter(reviewers__in=[self.user]).update(is_complete=True)

        # item (reviewed), revision: stale, reviewer: other
        self.item17 = item.make()
        self.item17revs = revision.make(item=self.item17, _quantity=2)
        self.item17revs[0].reviewers.add(self.lawyer)
        self.item17revs[0].reviewdocument_set.filter(reviewers__in=[self.lawyer]).update(is_complete=True)

        # item (reviewed, completed), revision: stale, reviewer: other
        self.item18 = item.make(is_complete=True)
        self.item18revs = revision.make(item=self.item18, _quantity=2)
        self.item18revs[0].reviewers.add(self.lawyer)
        self.item18revs[0].reviewdocument_set.filter(reviewers__in=[self.lawyer]).update(is_complete=True)

        # item (in review), revision: current, reviewer: user
        self.item19 = item.make()
        self.item19revs = revision.make(item=self.item19, _quantity=2)
        self.item19revs[1].reviewers.add(self.user)

        # item (in review, completed), revision: current, reviewer: user
        self.item20 = item.make(is_complete=True)
        self.item20revs = revision.make(item=self.item20, _quantity=2)
        self.item20revs[1].reviewers.add(self.user)

        # item (in review), revision: current, reviewer: other
        self.item21 = item.make()
        self.item21revs = revision.make(item=self.item21, _quantity=2)
        self.item21revs[1].reviewers.add(self.lawyer)

        # item (in review, completed), revision: current, reviewer: other
        self.item22 = item.make(is_complete=True)
        self.item22revs = revision.make(item=self.item22, _quantity=2)
        self.item22revs[1].reviewers.add(self.lawyer)

        # item (reviewed), revision: current, reviewer: user
        self.item23 = item.make()
        self.item23revs = revision.make(item=self.item23, _quantity=2)
        self.item23revs[1].reviewers.add(self.user)
        self.item23revs[1].reviewdocument_set.filter(reviewers__in=[self.user]).update(is_complete=True)

        # item (reviewed, completed), revision: current, reviewer: user
        self.item24 = item.make(is_complete=True)
        self.item24revs = revision.make(item=self.item24, _quantity=2)
        self.item24revs[1].reviewers.add(self.user)
        self.item24revs[1].reviewdocument_set.filter(reviewers__in=[self.user]).update(is_complete=True)

        # item (reviewed), revision: current, reviewer: other
        self.item25 = item.make()
        self.item25revs = revision.make(item=self.item25, _quantity=2)
        self.item25revs[1].reviewers.add(self.lawyer)
        self.item25revs[1].reviewdocument_set.filter(reviewers__in=[self.lawyer]).update(is_complete=True)

        # item (reviewed, completed), revision: current, reviewer: other
        self.item26 = item.make(is_complete=True)
        self.item26revs = revision.make(item=self.item26, _quantity=2)
        self.item26revs[1].reviewers.add(self.lawyer)
        self.item26revs[1].reviewdocument_set.filter(reviewers__in=[self.lawyer]).update(is_complete=True)

        """
        Needs Signing
        """
        # item (needs signing), revision: stale, signatory: user
        self.item27 = item.make()
        self.item27revs = revision.make(item=self.item27, _quantity=2)
        self.item27revs[0].signers.add(self.user)

        # item (needs signing, completed), revision: stale, signatory: user
        self.item28 = item.make(is_complete=True)
        self.item28revs = revision.make(item=self.item28, _quantity=2)
        self.item28revs[0].signers.add(self.user)

        # item (needs signing), revision: stale, signatory: other
        self.item29 = item.make()
        self.item29revs = revision.make(item=self.item29, _quantity=2)
        self.item29revs[0].signers.add(self.lawyer)

        # item (needs signing, completed), revision: stale, signatory: other
        self.item30 = item.make(is_complete=True)
        self.item30revs = revision.make(item=self.item30, _quantity=2)
        self.item30revs[0].signers.add(self.lawyer)

        # item (signed), revision: stale, signatory: user
        self.item31 = item.make()
        self.item31revs = revision.make(item=self.item31, _quantity=2)
        self.item31revs[0].signers.add(self.user)
        self.item31signs = self.get_signed_request(self.item31revs[0], self.user)

        # item (signed, completed), revision: stale, signatory: user
        self.item32 = item.make(is_complete=True)
        self.item32revs = revision.make(item=self.item32, _quantity=2)
        self.item32revs[0].signers.add(self.user)
        self.item32signs = self.get_signed_request(self.item32revs[0], self.user)

        # item (signed), revision: stale, signatory: other
        self.item33 = item.make()
        self.item33revs = revision.make(item=self.item33, _quantity=2)
        self.item33revs[0].signers.add(self.lawyer)
        self.item33signs = self.get_signed_request(self.item33revs[0], self.lawyer)

        # item (signed, completed), revision: stale, signatory: other
        self.item34 = item.make(is_complete=True)
        self.item34revs = revision.make(item=self.item34, _quantity=2)
        self.item34revs[0].signers.add(self.lawyer)
        self.item34signs = self.get_signed_request(self.item34revs[0], self.lawyer)

        # item (all signed), revision: stale, signatory: user
        self.item35 = item.make()
        self.item35revs = revision.make(item=self.item35, _quantity=2)
        self.item35revs[0].signers.add(self.user)
        self.item35signs = self.get_signed_request(self.item35revs[0], self.user)
        self.item35revs[0].primary_signdocument.complete()

        # item (all signed, completed), revision: stale, signatory: user
        self.item36 = item.make(is_complete=True)
        self.item36revs = revision.make(item=self.item36, _quantity=2)
        self.item36revs[0].signers.add(self.user)
        self.item36signs = self.get_signed_request(self.item36revs[0], self.user)
        self.item36revs[0].primary_signdocument.complete()

        # item (all signed), revision: stale, signatory: other
        self.item37 = item.make()
        self.item37revs = revision.make(item=self.item37, _quantity=2)
        self.item37revs[0].signers.add(self.lawyer)
        self.item37signs = self.get_signed_request(self.item37revs[0], self.lawyer)
        self.item37revs[0].primary_signdocument.complete()

        # item (all signed, completed), revision: stale, signatory: other
        self.item38 = item.make(is_complete=True)
        self.item38revs = revision.make(item=self.item38, _quantity=2)
        self.item38revs[0].signers.add(self.lawyer)
        self.item38signs = self.get_signed_request(self.item38revs[0], self.lawyer)
        self.item38revs[0].primary_signdocument.complete()

        # item (needs signing), revision: current, signatory: user
        self.item39 = item.make()
        self.item39revs = revision.make(item=self.item39, _quantity=2)
        self.item39revs[1].signers.add(self.user)

        # item (needs signing, completed), revision: current, signatory: user
        self.item40 = item.make(is_complete=True)
        self.item40revs = revision.make(item=self.item40, _quantity=2)
        self.item40revs[1].signers.add(self.user)

        # item (needs signing), revision: current, signatory: other
        self.item41 = item.make()
        self.item41revs = revision.make(item=self.item41, _quantity=2)
        self.item41revs[1].signers.add(self.lawyer)

        # item (needs signing, completed), revision: current, signatory: other
        self.item42 = item.make(is_complete=True)
        self.item42revs = revision.make(item=self.item42, _quantity=2)
        self.item42revs[1].signers.add(self.lawyer)

        # item (signed), revision: current, signatory: user
        self.item43 = item.make()
        self.item43revs = revision.make(item=self.item43, _quantity=2)
        self.item43revs[1].signers.add(self.user)
        self.item43signs = self.get_signed_request(self.item43revs[1], self.user)

        # item (signed, completed), revision: current, signatory: user
        self.item44 = item.make(is_complete=True)
        self.item44revs = revision.make(item=self.item44, _quantity=2)
        self.item44revs[1].signers.add(self.user)
        self.item44signs = self.get_signed_request(self.item44revs[1], self.user)

        # item (signed), revision: current, signatory: other
        self.item45 = item.make()
        self.item45revs = revision.make(item=self.item45, _quantity=2)
        self.item45revs[1].signers.add(self.lawyer)
        self.item45signs = self.get_signed_request(self.item45revs[1], self.lawyer)

        # item (signed, completed), revision: current, signatory: other
        self.item46 = item.make(is_complete=True)
        self.item46revs = revision.make(item=self.item46, _quantity=2)
        self.item46revs[1].signers.add(self.lawyer)
        self.item46signs = self.get_signed_request(self.item46revs[1], self.lawyer)

        # item (all signed), revision: current, signatory: user
        self.item47 = item.make()
        self.item47revs = revision.make(item=self.item47, _quantity=2)
        self.item47revs[1].signers.add(self.user)
        self.item47signs = self.get_signed_request(self.item47revs[1], self.user)
        self.item47revs[1].primary_signdocument.complete()

        # item (all signed, completed), revision: current, signatory: user
        self.item48 = item.make(is_complete=True)
        self.item48revs = revision.make(item=self.item48, _quantity=2)
        self.item48revs[1].signers.add(self.user)
        self.item48signs = self.get_signed_request(self.item48revs[1], self.user)
        self.item48revs[1].primary_signdocument.complete()

        # item (all signed), revision: current, signatory: other
        self.item49 = item.make()
        self.item49revs = revision.make(item=self.item49, _quantity=2)
        self.item49revs[1].signers.add(self.lawyer)
        self.item49signs = self.get_signed_request(self.item49revs[1], self.lawyer)
        self.item49revs[1].primary_signdocument.complete()

        # item (all signed, completed), revision: current, signatory: other
        self.item50 = item.make(is_complete=True)
        self.item50revs = revision.make(item=self.item50, _quantity=2)
        self.item50revs[1].signers.add(self.lawyer)
        self.item50signs = self.get_signed_request(self.item50revs[1], self.lawyer)
        self.item50revs[1].primary_signdocument.complete()

    def test_requests(self):
        object_set = Item.objects.my_requests(self.user)
        # check we have the breakdown
        self.assertItemsEqual(object_set.keys(), ['count', 'items', 'tasks'])
        # set the requests object
        requests = object_set.get('items')

        self.assertEqual(len(requests), 3)
        self.assertTrue(self.item7 in requests)
        self.assertTrue(self.item19 in requests)
        self.assertTrue(self.item39 in requests)

        object_set = Item.objects.my_requests(self.user, completed=True)
        self.assertItemsEqual(object_set.keys(), ['count', 'items', 'tasks'])
        # set the requests object
        completed_requests = object_set.get('items')

        self.assertEqual(len(completed_requests), 9)
        self.assertTrue(self.item8 in completed_requests)
        self.assertTrue(self.item20 in completed_requests)
        self.assertTrue(self.item23 in completed_requests)
        self.assertTrue(self.item24 in completed_requests)
        self.assertTrue(self.item40 in completed_requests)
        self.assertTrue(self.item43 in completed_requests)
        self.assertTrue(self.item44 in completed_requests)
        self.assertTrue(self.item47 in completed_requests)
        self.assertTrue(self.item48 in completed_requests)

    def get_signed_request(self, revision, user):
        return mommy.make('hello_sign.HelloSignRequest',
            content_object_type=ContentType.objects.get_for_model(revision.primary_signdocument),
            object_id=revision.primary_signdocument.pk,
            data={
                'signature_request': {
                    'signatures': [{
                        'signer_email_address': user.email,
                        'signed_at': datetime.utcnow()
                    }]
                }
            }
        )
