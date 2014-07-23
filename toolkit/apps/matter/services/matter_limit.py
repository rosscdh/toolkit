# -*- coding: utf-8 -*-
from django.conf import settings
from payments.models import CurrentSubscription


class BillingMatterLimitService(object):
    def __init__(self, user):
        self.enabled = settings.BILLING_MATTER_LIMIT.get('ENABLED', True)
        self.user = user
        self.num_matters = self.user.workspace_set.all().count()

    @property
    def has_plan(self):
        try:
            return CurrentSubscription.objects.get(customer=self.user)
        except CurrentSubscription.DoesNotExist:
            return False

    @property
    def can_create_new_matter(self):
        # if we have disabled the limits then always allow user to create matters
        if self.enabled is False:
            return True
        # allow for excluded users
        if self.user.email in settings.BILLING_MATTER_LIMIT.get('EXCLUDE_EMAILS', ()):
            return True
        # user is on a plan
        if self.has_plan is not False:
            return True
        # otherwise appliy the logic
        return settings.BILLING_MATTER_LIMIT.get('MAX_FREE_MATTERS') > self.num_matters