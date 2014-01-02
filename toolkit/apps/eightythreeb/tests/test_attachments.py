# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios


class AttachmentQuerysetAndObjectDeleteTest(BaseScenarios, TestCase):
    def setUp(self):
        super(AttachmentQuerysetAndObjectDeleteTest, self).setUp()
        self.basic_workspace()

        self.eightythreeb.attachment_set.add(mommy.make('eightythreeb.Attachment', eightythreeb=self.eightythreeb))
        self.eightythreeb.attachment_set.add(mommy.make('eightythreeb.Attachment', eightythreeb=self.eightythreeb))
        self.eightythreeb.attachment_set.add(mommy.make('eightythreeb.Attachment', eightythreeb=self.eightythreeb))

    def test_object_delete(self):
        """
        Test the object instance delete override works
        """
        # we have 2 attachments
        self.assertEqual(3, self.eightythreeb.attachment_set.all().count())
        # delete a single object
        self.eightythreeb.attachment_set.all()[0].delete()
        # we should now have 2 active attachments
        self.assertEqual(2, self.eightythreeb.attachment_set.all().count())
        # and 1 deleted
        self.assertEqual(1, self.eightythreeb.attachment_set.deleted().count())

    def test_queryset_delete(self):
        """
        Test the Queryset delete override works
        """
        # we have 2 attachments
        self.assertEqual(3, self.eightythreeb.attachment_set.all().count())
        # delete a single object
        self.eightythreeb.attachment_set.all().delete()
        # we should now have 0 active attachments
        self.assertEqual(0, self.eightythreeb.attachment_set.all().count())
        # and 3 deleted
        self.assertEqual(3, self.eightythreeb.attachment_set.deleted().count())
