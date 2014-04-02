from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios

from ..managers import ItemManager
from ..models import Item

import uuid


class ItemManagerTest(BaseScenarios, TestCase):
    def setUp(self):
        super(ItemManagerTest, self).setUp()
        self.basic_workspace()

    def test_my_requests_come_in_expected_order(self):
        # item, revisions: 0
        item1 = mommy.make('item.Item', matter=self.matter)


        # item, requested, revisions: 0, user: customer
        item2 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4(), is_requested=True, responsible_party=self.user)

        # item, requested, revisions: 0, user: lawyer
        item3 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4(), is_requested=True, responsible_party=self.lawyer)

        # item, reviewer: user, revision: stale
        item5 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev5a = mommy.make('attachment.Revision', item=item5, reviewers=[self.user])
        rev5b = mommy.make('attachment.Revision', item=item5)

        # item, reviewer: lawyer, revision: stale
        item6 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev6a = mommy.make('attachment.Revision', item=item6, reviewers=[self.lawyer])
        rev6b = mommy.make('attachment.Revision', item=item6)

        # item, reviewer: user, revision: current
        item7 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev7a = mommy.make('attachment.Revision', item=item7)
        rev7b = mommy.make('attachment.Revision', item=item7, reviewers=[self.user])

        # item, reviewer: lawyer, revision: current
        item8 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev8a = mommy.make('attachment.Revision', item=item8)
        rev8b = mommy.make('attachment.Revision', item=item8, reviewers=[self.lawyer])

        # item, signatory: user, revision: stale
        item9 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev9a = mommy.make('attachment.Revision', item=item9, signers=[self.user])
        rev9b = mommy.make('attachment.Revision', item=item9)

        # item, signatory: lawyer, revision: stale
        item10 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev10a = mommy.make('attachment.Revision', item=item10, signers=[self.lawyer])
        rev10b = mommy.make('attachment.Revision', item=item10)

        # item, signatory: user, revision: current
        item11 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev11a = mommy.make('attachment.Revision', item=item11)
        rev11b = mommy.make('attachment.Revision', item=item11, signers=[self.user])

        # item, signatory: lawyer, revision: current
        item12 = mommy.make('item.Item', matter=self.matter, slug=uuid.uuid4())
        rev12a = mommy.make('attachment.Revision', item=item12)
        rev12b = mommy.make('attachment.Revision', item=item12, signers=[self.lawyer])

        my_requests = Item.objects.my_requests(self.user)

        self.assertEquals(my_requests.count(), 3)
        self.assertTrue(item2 in my_requests)
        self.assertTrue(item7 in my_requests)
        self.assertTrue(item11 in my_requests)
