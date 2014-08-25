# -*- coding: UTF-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios


class LastCommentedByTest(BaseScenarios, TestCase):
    def setUp(self):
        super(LastCommentedByTest, self).setUp()
        self.basic_workspace()
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item', category=None)

    def test_unprivileged_last_comment(self):
        self.item.set_last_comment_by(is_public=True, user=self.user)
        self.item.set_last_comment_by(is_public=False, user=self.lawyer)
        self.item.save(update_fields=['data'])

        #
        # A public user should see the public comment: CT = customer test (user)
        #
        self.assertEqual(self.item.last_comment_by(is_public=True), 'CT')
        #
        # A colleage should see the private comment: LT = lawyer test (user)
        #
        self.assertEqual(self.item.last_comment_by(is_public=False), 'LT')