from django.test import TestCase

from model_mommy import mommy
from model_mommy.recipe import Recipe

from toolkit.casper.workflow_case import BaseScenarios

from ..managers import ItemManager
from ..models import Item

import uuid


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
        self.item31revs[0].signdocument_set.filter(signers__in=[self.user]).update(is_complete=True)

        # item (signed, completed), revision: stale, signatory: user
        self.item32 = item.make(is_complete=True)
        self.item32revs = revision.make(item=self.item32, _quantity=2)
        self.item32revs[0].signers.add(self.user)
        self.item32revs[0].signdocument_set.filter(signers__in=[self.user]).update(is_complete=True)

        # item (signed), revision: stale, signatory: other
        self.item33 = item.make()
        self.item33revs = revision.make(item=self.item33, _quantity=2)
        self.item33revs[0].signers.add(self.lawyer)
        self.item33revs[0].signdocument_set.filter(signers__in=[self.lawyer]).update(is_complete=True)

        # item (signed, completed), revision: stale, signatory: other
        self.item34 = item.make(is_complete=True)
        self.item34revs = revision.make(item=self.item34, _quantity=2)
        self.item34revs[0].signers.add(self.lawyer)
        self.item34revs[0].signdocument_set.filter(signers__in=[self.lawyer]).update(is_complete=True)

        # item (needs signing), revision: current, signatory: user
        self.item35 = item.make()
        self.item35revs = revision.make(item=self.item35, _quantity=2)
        self.item35revs[1].signers.add(self.user)

        # item (needs signing, completed), revision: current, signatory: user
        self.item36 = item.make(is_complete=True)
        self.item36revs = revision.make(item=self.item36, _quantity=2)
        self.item36revs[1].signers.add(self.user)

        # item (needs signing), revision: current, signatory: other
        self.item37 = item.make()
        self.item37revs = revision.make(item=self.item37, _quantity=2)
        self.item37revs[1].signers.add(self.lawyer)

        # item (needs signing, completed), revision: current, signatory: other
        self.item38 = item.make(is_complete=True)
        self.item38revs = revision.make(item=self.item38, _quantity=2)
        self.item38revs[1].signers.add(self.lawyer)

        # item (signed), revision: current, signatory: user
        self.item39 = item.make()
        self.item39revs = revision.make(item=self.item39, _quantity=2)
        self.item39revs[1].signers.add(self.user)
        self.item39revs[1].signdocument_set.filter(signers__in=[self.user]).update(is_complete=True)

        # item (signed, completed), revision: current, signatory: user
        self.item40 = item.make(is_complete=True)
        self.item40revs = revision.make(item=self.item40, _quantity=2)
        self.item40revs[1].signers.add(self.user)
        self.item40revs[1].signdocument_set.filter(signers__in=[self.user]).update(is_complete=True)

        # item (signed), revision: current, signatory: other
        self.item41 = item.make()
        self.item41revs = revision.make(item=self.item41, _quantity=2)
        self.item41revs[1].signers.add(self.lawyer)
        self.item41revs[1].signdocument_set.filter(signers__in=[self.lawyer]).update(is_complete=True)

        # item (signed, completed), revision: current, signatory: other
        self.item42 = item.make(is_complete=True)
        self.item42revs = revision.make(item=self.item42, _quantity=2)
        self.item42revs[1].signers.add(self.lawyer)
        self.item42revs[1].signdocument_set.filter(signers__in=[self.lawyer]).update(is_complete=True)

    def test_requests(self):
        requests = Item.objects.my_requests(self.user)
        self.assertEqual(requests.count(), 3)
        self.assertTrue(self.item7 in requests)
        self.assertTrue(self.item19 in requests)
        self.assertTrue(self.item35 in requests)

        completed_requests = Item.objects.my_requests(self.user, completed=True)
        self.assertEqual(completed_requests.count(), 7)
        self.assertTrue(self.item8 in completed_requests)
        self.assertTrue(self.item20 in completed_requests)
        self.assertTrue(self.item23 in completed_requests)
        self.assertTrue(self.item24 in completed_requests)
        self.assertTrue(self.item36 in completed_requests)
        self.assertTrue(self.item39 in completed_requests)
        self.assertTrue(self.item40 in completed_requests)
