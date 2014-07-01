from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios

from ..models import Revision


class RevisionManagerTest(BaseScenarios, TestCase):
    def setUp(self):
        super(RevisionManagerTest, self).setUp()
        self.basic_workspace()

        self.item1 = mommy.make('item.Item', matter=self.matter)
        self.item2 = mommy.make('item.Item', matter=self.matter)

    def test_current(self):
        self.assertEquals(Revision.objects.current().count(), 0)

        revision1a = mommy.make('attachment.Revision', item=self.item1, is_current=True)
        revision2a = mommy.make('attachment.Revision', item=self.item2, is_current=False)

        self.assertEquals(Revision.objects.current().count(), 1)
        self.assertEquals(Revision.objects.current()[0], revision1a)

        revision1b = mommy.make('attachment.Revision', item=self.item1, is_current=False)
        revision2b = mommy.make('attachment.Revision', item=self.item2, is_current=True)

        self.assertEquals(Revision.objects.current().count(), 2)
        self.assertEquals(Revision.objects.current()[0], revision1a)
        self.assertEquals(Revision.objects.current()[1], revision2b)

    def test_visible(self):
        self.assertEquals(Revision.objects.visible(self.user, self.matter).count(), 0)

        # test if I see revisions I uploaded
        mommy.make('attachment.Revision', item=self.item1, uploaded_by=self.user)
        self.assertEquals(Revision.objects.visible(self.user, self.matter).count(), 1)

        # test if I see revisions I shall sign
        revision2 = mommy.make('attachment.Revision', item=self.item1)
        revision2.signers.add(self.user)
        self.assertEquals(Revision.objects.visible(self.user, self.matter).count(), 2)

        # test if i see revisions I shall review
        revision3 = mommy.make('attachment.Revision', item=self.item1)
        revision3.reviewers.add(self.user)
        self.assertEquals(Revision.objects.visible(self.user, self.matter).count(), 3)
