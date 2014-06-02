from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios


class PermissionTest(BaseScenarios, TestCase):
    def setUp(self):
        super(PermissionTest, self).setUp()
        self.basic_workspace()
        self.item = mommy.make('item.Item', matter=self.matter)

    def test_add_perm(self):
        user1 = mommy.make('auth.User', username='user1')
        user2 = mommy.make('auth.User', username='user2')

        self.matter.participants.add(user1)
        self.assertEqual(user1.has_perm('item.read_item', self.item), True)
        self.assertEqual(user2.has_perm('item.read_item', self.item), False)