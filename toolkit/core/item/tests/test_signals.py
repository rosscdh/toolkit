from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios


class EnsureOpenRequestsCountUpdatedTest(BaseScenarios, TestCase):
    def setUp(self):
        super(EnsureOpenRequestsCountUpdatedTest, self).setUp()
        self.basic_workspace()

    def test(self):
        item = mommy.make('item.Item', matter=self.matter, is_requested=True)

        self.assertEqual(self.user.profile.get_open_requests_count(), 0)

        item.responsible_party = self.user
        item.save(update_fields=['responsible_party'])
        self.assertEqual(self.user.profile.get_open_requests_count(), 1)

        item.is_complete = True
        item.save(update_fields=['is_complete'])
        self.assertEqual(self.user.profile.get_open_requests_count(), 0)
