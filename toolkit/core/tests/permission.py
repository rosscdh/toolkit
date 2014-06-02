from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios


class PermissionTest(BaseScenarios, TestCase):
    def setUp(self):
        super(PermissionTest, self).setUp()
        self.basic_workspace()
        self.item = mommy.make('item.Item', matter=self.matter)

    def test_add_perm(self):
        self.assertEqual(self.lawyer.has_perm('workspace.manage_participants', self.matter), True)