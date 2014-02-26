import datetime

from django.test import TestCase

from toolkit.casper import BaseScenarios

from ..models import EightyThreeB


class EightyThreeBTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(EightyThreeBTestCase, self).setUp()
        self.basic_workspace()

    def test_get_edit_url(self):
        eightythreeb = EightyThreeB(workspace=self.workspace, slug='e0c545082d1241849be039e338e47a0f')
        self.assertEquals(eightythreeb.get_edit_url(), '/workspace/lawpal-test/tool/83b-election-letters/e0c545082d1241849be039e338e47a0f/edit/')

    def test_has_expired(self):
        # Date in future (not complete)
        self.eightythreeb.status = EightyThreeB.STATUS.lawyer_complete_form
        self.eightythreeb.filing_date = datetime.date.today() + datetime.timedelta(days=5)
        self.assertFalse(self.eightythreeb.has_expired)

        # Date in future (complete)
        self.eightythreeb.status = EightyThreeB.STATUS.complete
        self.assertFalse(self.eightythreeb.has_expired)

        # Today's date (not complete)
        self.eightythreeb.status = EightyThreeB.STATUS.lawyer_complete_form
        self.eightythreeb.filing_date = datetime.date.today()
        self.assertFalse(self.eightythreeb.has_expired)

        # Today's date (complete)
        self.eightythreeb.status = EightyThreeB.STATUS.complete
        self.assertFalse(self.eightythreeb.has_expired)

        # Date in past (not complete)
        self.eightythreeb.status = EightyThreeB.STATUS.lawyer_complete_form
        self.eightythreeb.filing_date = datetime.date.today() - datetime.timedelta(days=5)
        self.assertTrue(self.eightythreeb.has_expired)

        # Date in past (complete)
        self.eightythreeb.status = EightyThreeB.STATUS.complete
        self.assertFalse(self.eightythreeb.has_expired)
