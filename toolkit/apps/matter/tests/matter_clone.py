# -*- coding: utf-8 -*-
from django.test import TestCase

from toolkit.test_runner import DEMO_DOC as TEST_PDF_DEST_PATH

from model_mommy import mommy

from ..services import MatterCloneService, DemoMatterCloneService

import os
import datetime


class BaseMatterClone(TestCase):
    subject = None
    test_pdf_base_name = os.path.basename(TEST_PDF_DEST_PATH)

    def setUp(self):
        self.lawyer = mommy.make('auth.User', username='test-lawyer', first_name='Lawyer', last_name='Test', email='test+lawyer@lawpal.com')

        # matter to clone
        self.source = mommy.make('workspace.Workspace', name='Source Matter to be copied', lawyer=self.lawyer)
        self.source.categories = ['A', 'B', 'C']

        # items to clone
        self.item = mommy.make('item.Item', matter=self.source, name='Test Item from Source No.1', category=None)
        mommy.make('attachment.Revision', executed_file=TEST_PDF_DEST_PATH, slug=None, item=self.item, uploaded_by=self.lawyer)
        
        self.item2 = mommy.make('item.Item', matter=self.source, name='Test Item from Source No.2', category=None)
        mommy.make('attachment.Revision', executed_file=TEST_PDF_DEST_PATH, slug=None, item=self.item2, uploaded_by=self.lawyer)

        self.assertEqual(self.source.item_set.all().count(), 2)
        # source items have their original documents
        self.assertEqual(self.item.revision_set.all().count(), 1)
        self.assertEqual(self.item2.revision_set.all().count(), 1)

        self.target_matter = mommy.make('workspace.Workspace', name='Target Matter to get items', lawyer=self.lawyer)
        self.assertEqual(self.target_matter.item_set.all().count(), 0)

        service = self.subject(source_matter=self.source,
                               target_matter=self.target_matter)
        service.process()  # process the objects

        # test we now have the items
        self.assertEqual(self.target_matter.item_set.all().count(), 2)



class MatterCloneServiceTest(BaseMatterClone):
    """
    The Matter clone services Copies a matter and its items but NOT its revisions
    Its tests for revisions are the exact opposite of the DemoMatterCloneService
    """
    subject = MatterCloneService

    def test_clone_service(self):
        # self.target_matter items dont have any documents (revision)
        self.assertTrue(all(i.latest_revision is None for i in self.target_matter.item_set.all()))

        # self.target_matter items dont have any documents
        self.assertTrue(all(i.revision_set.all().count() == 0 for i in self.target_matter.item_set.all()))
        self.assertEqual(self.item.revision_set.model.objects.filter(item__in=self.target_matter.item_set.all()).count(), 0)

        # test that the slugs are all unique
        self.assertTrue(all(str(i.slug) not in self.source.item_set.all().values('slug') for i in self.target_matter.item_set.all()))
        self.assertTrue(all(str(i.pk) not in self.source.item_set.all().values('pk') for i in self.target_matter.item_set.all()))

        # test that the source also still has them
        self.assertEqual(self.source.item_set.all().count(), 2)
        # SOURCE items still has their original documents
        self.assertEqual(self.item.revision_set.all().count(), 1)
        self.assertEqual(self.item2.revision_set.all().count(), 1)

        # test the self.target_matter matter has the cloned dict
        self.assertTrue(type(self.target_matter.data.get('cloned')), dict)
        self.assertEqual(self.target_matter.data.get('cloned').keys(), ['date_cloned', 'num_items'])
        self.assertEqual(type(self.target_matter.data.get('cloned').get('date_cloned')), datetime.datetime)
        self.assertEqual(self.target_matter.data.get('cloned').get('num_items'), 2)

        # test the self.target_matter matter has the caegories preserved and in correct order
        self.assertEqual(self.target_matter.categories, self.source.categories)


class DemoMatterCloneServiceTest(BaseMatterClone):
    """
    The Demo clone services Copies the revision documents to allow the user a chance
    to explore the system. Is tests relating to the revision documents are the exact
    opposite of what the normal MatterCloneService does
    """
    subject = DemoMatterCloneService

    def test_demo_clone_service(self):
        # self.target_matter items DO have a latest revision
        self.assertTrue(all(i.latest_revision is not None for i in self.target_matter.item_set.all()))

        #
        # self.target_matter items DOES HAVE documents (Unlike the MatterCloneService)
        #
        self.assertTrue(all(i.revision_set.all().count() == 1 for i in self.target_matter.item_set.all()))
        self.assertEqual(self.item.revision_set.model.objects.filter(item__in=self.target_matter.item_set.all()).count(), 2)

        #
        # Test that the documents ahve been cloned and renamed
        #
        for i in self.target_matter.item_set.all():
            for r in i.revision_set.all():
                new_file_name = os.path.basename(r.executed_file.name)
                # test the file has been renamed
                self.assertNotEqual(new_file_name, self.test_pdf_base_name)
                # test the new_fiename is built with the matter pk in it to make it unique
                self.assertEqual(new_file_name, '%s-%s' % (self.target_matter.pk, self.test_pdf_base_name,))

        # test that the slugs are all unique
        self.assertTrue(all(str(i.slug) not in self.source.item_set.all().values('slug') for i in self.target_matter.item_set.all()))
        self.assertTrue(all(str(i.pk) not in self.source.item_set.all().values('pk') for i in self.target_matter.item_set.all()))

        # test that the source also still has them
        self.assertEqual(self.source.item_set.all().count(), 2)
        # SOURCE items still has their original documents
        self.assertEqual(self.item.revision_set.all().count(), 1)
        self.assertEqual(self.item2.revision_set.all().count(), 1)

        # test the self.target_matter matter has the cloned dict
        self.assertTrue(type(self.target_matter.data.get('is_demo')), True)
        self.assertTrue(type(self.target_matter.data.get('cloned')), dict)
        self.assertEqual(self.target_matter.data.get('cloned').keys(), ['date_cloned', 'num_items'])
        self.assertEqual(type(self.target_matter.data.get('cloned').get('date_cloned')), datetime.datetime)
        self.assertEqual(self.target_matter.data.get('cloned').get('num_items'), 2)

        # test the self.target_matter matter has the caegories preserved and in correct order
        self.assertEqual(self.target_matter.categories, self.source.categories)
