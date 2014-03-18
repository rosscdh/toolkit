# -*- coding: utf-8 -*-
from django.test import TestCase
from model_mommy import mommy

from ..services import MatterCloneService


class MatterCloneTest(TestCase):
    def setUp(self):
        self.subject = MatterCloneService
        # matter to clone
        self.source = mommy.make('workspace.Workspace', name='Source Matter to be copied')
        # items to clone
        mommy.make('item.Item', matter=self.source, name='Test Item from Source No.1', category=None)
        mommy.make('item.Item', matter=self.source, name='Test Item from Source No.2', category=None)

    def test_clone_service(self):
        self.assertEqual(self.source.item_set.all().count(), 2)

        target = mommy.make('workspace.Workspace', name='Target Matter to get items')
        self.assertEqual(target.item_set.all().count(), 0)

        service = self.subject(source_matter=self.source,
                               target_matter=target)
        service.process()  # process the objects

        # test we now have the items
        self.assertEqual(target.item_set.all().count(), 2)

        # test that the slugs are all unique
        self.assertTrue(all(str(i.slug) not in self.source.item_set.all().values('slug') for i in target.item_set.all()))

        # test that the source also still has them
        self.assertEqual(self.source.item_set.all().count(), 2)