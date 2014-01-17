# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios


class AttachmentQuerysetAndObjectDeleteTest(BaseScenarios, TestCase):
    def setUp(self):
        super(AttachmentQuerysetAndObjectDeleteTest, self).setUp()
        self.basic_workspace()
        self.eightythreeb.status = self.eightythreeb.STATUS_83b.copy_uploaded
        self.eightythreeb.save(update_fields=['status'])

    def add_attachments(self):
        self.eightythreeb.attachment_set.add(mommy.make('eightythreeb.Attachment', eightythreeb=self.eightythreeb))
        self.eightythreeb.attachment_set.add(mommy.make('eightythreeb.Attachment', eightythreeb=self.eightythreeb))
        self.eightythreeb.attachment_set.add(mommy.make('eightythreeb.Attachment', eightythreeb=self.eightythreeb))

    def test_object_has_no_copy_uploaded_marker(self):
        """
        Test that when we have no attachmetns we have no copy_uploaded marker
        """
        self.assertTrue('copy_uploaded' not in self.eightythreeb.data['markers']) # should not be present

    def test_object_has_copy_uploaded_marker(self):
        """
        Test that once an attachment is added we have the copy marker
        """
        self.add_attachments() # attach the attachments
        self.assertTrue('copy_uploaded' in self.eightythreeb.data['markers'])

    def test_object_delete(self):
        """
        Test the object instance delete override works
        """
        self.add_attachments() # attach the attachments

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
        self.add_attachments() # attach the attachments

        # we have 2 attachments
        self.assertEqual(3, self.eightythreeb.attachment_set.all().count())
        # delete a single object
        self.eightythreeb.attachment_set.all().delete()
        # we should now have 0 active attachments
        self.assertEqual(0, self.eightythreeb.attachment_set.all().count())
        # and 3 deleted
        self.assertEqual(3, self.eightythreeb.attachment_set.deleted().count())

    def test_marker_is_removed_when_attachments_is_zero(self):
        """
        Ensure that if we have attachments and we remove them all
        then the copy_uploaded marker is removed
        """
        self.add_attachments() # attach the attachments
        self.assertTrue('copy_uploaded' in self.eightythreeb.data['markers'])

        # now remove all the markers
        for a in self.eightythreeb.attachment_set.all():
            #
            # We have to delete individually as there is no delete signal sent for queryset deletes
            # i.e. self.eightythreeb.attachment_set.all().delete() and self.eightythreeb.attachment_set.all().update(is_deleted=True)
            # Will not work
            #
            a.delete()
        # now the copy_uploaded marker should be gone
        self.assertTrue('copy_uploaded' not in self.eightythreeb.data['markers'])
