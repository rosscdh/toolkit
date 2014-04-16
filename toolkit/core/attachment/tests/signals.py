from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios

from ..models import Revision


class EnsureOneCurrentRevisionTest(BaseScenarios, TestCase):
    def setUp(self):
        super(EnsureOneCurrentRevisionTest, self).setUp()
        self.basic_workspace()

        self.item1 = mommy.make('item.Item', matter=self.matter)
        self.item2 = mommy.make('item.Item', matter=self.matter)

    def test_is_current_updates(self):
        """There should only be one current revision for an item"""
        revision1a = mommy.make('attachment.Revision', item=self.item1, is_current=True)
        revision2a = mommy.make('attachment.Revision', item=self.item2, is_current=False)

        # Set a revision to current, where there's no other current revisions
        revision2a.is_current = True
        revision2a.save(update_fields=['is_current'])

        self.assertTrue(Revision.objects.get(pk=revision1a.pk).is_current)
        self.assertTrue(Revision.objects.get(pk=revision2a.pk).is_current)

        revision1b = mommy.make('attachment.Revision', item=self.item1, is_current=False)
        revision2b = mommy.make('attachment.Revision', item=self.item2, is_current=False)

        # Set a revision to current, where there's other revisions
        revision1b.is_current = True
        revision1b.save(update_fields=['is_current'])

        self.assertFalse(Revision.objects.get(pk=revision1a.pk).is_current)
        self.assertTrue(Revision.objects.get(pk=revision2a.pk).is_current)
        self.assertTrue(Revision.objects.get(pk=revision1b.pk).is_current)
        self.assertFalse(Revision.objects.get(pk=revision2b.pk).is_current)

        revision2b.is_current = True
        revision2b.save(update_fields=['is_current'])

        self.assertFalse(Revision.objects.get(pk=revision1a.pk).is_current)
        self.assertFalse(Revision.objects.get(pk=revision2a.pk).is_current)
        self.assertTrue(Revision.objects.get(pk=revision1b.pk).is_current)
        self.assertTrue(Revision.objects.get(pk=revision2b.pk).is_current)
