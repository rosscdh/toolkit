import datetime

from django.test import TestCase

from toolkit.casper import BaseScenarios

from ..models import EightyThreeB


class EightyThreeBTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(EightyThreeBTestCase, self).setUp()
        self.basic_workspace()

    def test_is_expired(self):
        # Date in future (not complete)
        self.eightythreeb.status = EightyThreeB.STATUS.lawyer_complete_form
        self.eightythreeb.filing_date = datetime.date.today() + datetime.timedelta(days=5)
        self.assertFalse(self.eightythreeb.is_expired)

        # Date in future (complete)
        self.eightythreeb.status = EightyThreeB.STATUS.complete
        self.assertFalse(self.eightythreeb.is_expired)

        # Today's date (not complete)
        self.eightythreeb.status = EightyThreeB.STATUS.lawyer_complete_form
        self.eightythreeb.filing_date = datetime.date.today()
        self.assertFalse(self.eightythreeb.is_expired)

        # Today's date (complete)
        self.eightythreeb.status = EightyThreeB.STATUS.complete
        self.assertFalse(self.eightythreeb.is_expired)

        # Date in past (not complete)
        self.eightythreeb.status = EightyThreeB.STATUS.lawyer_complete_form
        self.eightythreeb.filing_date = datetime.date.today() - datetime.timedelta(days=5)
        self.assertTrue(self.eightythreeb.is_expired)

        # Date in past (complete)
        self.eightythreeb.status = EightyThreeB.STATUS.complete
        self.assertFalse(self.eightythreeb.is_expired)
