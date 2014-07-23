# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.utils import override_settings

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios
from ..services import BillingMatterLimitService

DEFAULT_BILLING_MATTER_LIMIT = {
    'ENABLED': True,
    'MAX_FREE_MATTERS': 1,
    'EXCLUDE_EMAILS': ('yael@lawpal.com',),
}

DISABLED_BILLING_MATTER_LIMIT = DEFAULT_BILLING_MATTER_LIMIT.copy()
DISABLED_BILLING_MATTER_LIMIT.update({
    'ENABLED': False,
})


class BillingMatterLimitServiceTest(BaseScenarios, TestCase):
    subject = BillingMatterLimitService

    def setUp(self):
        self.basic_workspace()

    def test_enabled_false(self):
        with override_settings(BILLING_MATTER_LIMIT=DISABLED_BILLING_MATTER_LIMIT):
            service = self.subject(user=self.lawyer)
            self.assertTrue(service.can_create_new_matter)  # user should be able to create as many as possible as we have disabled the check

    def test_excluded_emails(self):
        with override_settings(BILLING_MATTER_LIMIT=DEFAULT_BILLING_MATTER_LIMIT):
            service = self.subject(user=self.lawyer)
            self.assertFalse(service.can_create_new_matter)  # user should not be able to make matters as they are normal users
            # now with correct email
            self.lawyer.email = DEFAULT_BILLING_MATTER_LIMIT.get('EXCLUDE_EMAILS')[0]  # set to first email in list above
            service = self.subject(user=self.lawyer)
            self.assertTrue(service.can_create_new_matter)  # user should be able to create as many as possible as their email is excluded from test

    def test_user_has_too_many_plans(self):
        with override_settings(BILLING_MATTER_LIMIT=DEFAULT_BILLING_MATTER_LIMIT):
            # has too many matters already
            self.assertEqual(self.lawyer.workspace_set.all().count(), DEFAULT_BILLING_MATTER_LIMIT.get('MAX_FREE_MATTERS'))
            service = self.subject(user=self.lawyer)
            self.assertFalse(service.can_create_new_matter)

            # upgrades and can now proceed
            customer = mommy.make('payments.Customer', user=self.lawyer)
            subscription = mommy.make('payments.CurrentSubscription', customer=customer, cancel_at_period_end=True)
            service = self.subject(user=self.lawyer)
            self.assertTrue(service.can_create_new_matter)  # user should be able to create as many as possible as their email is excluded from test

    def test_user_has_paid_plan(self):
        with override_settings(BILLING_MATTER_LIMIT=DEFAULT_BILLING_MATTER_LIMIT):
            service = self.subject(user=self.lawyer)
            # initially they cant create a new matter
            self.assertFalse(service.can_create_new_matter)
            # but they upgrade and now they can
            customer = mommy.make('payments.Customer', user=self.lawyer)
            subscription = mommy.make('payments.CurrentSubscription', customer=customer, cancel_at_period_end=True)
            service = self.subject(user=self.lawyer)
            self.assertTrue(service.can_create_new_matter)  # user should be able to create as many as possible as their email is excluded from test
