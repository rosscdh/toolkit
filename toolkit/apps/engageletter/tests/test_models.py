from django.test import TestCase

from toolkit.casper import BaseScenarios

from ..models import EngagementLetter


class EngagementLetterTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(EngagementLetterTestCase, self).setUp()
        self.basic_workspace()

    def test_get_edit_url(self):
        engagement_letter = EngagementLetter(workspace=self.workspace, slug='e0c545082d1241849be039e338e47a0f')
        self.assertEquals(engagement_letter.get_edit_url(), '/workspace/lawpal-test/tool/engagement-letters/e0c545082d1241849be039e338e47a0f/edit/')
