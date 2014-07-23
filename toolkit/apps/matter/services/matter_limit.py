# -*- coding: utf-8 -*-
from django.conf import settings
from payments.models import Customer, CurrentSubscription

assert settings.BILLING_MATTER_LIMIT is not None, 'Please define settings.BILLING_MATTER_LIMIT = {}'

import logging
logger = logging.getLogger('django.request')


class BillingMatterLimitService(object):
    """
    Service to allow evaluation of user matter creation status
    """
    def __init__(self, user):
        self.enabled = settings.BILLING_MATTER_LIMIT.get('ENABLED', True)
        self.user = user
        self.num_matters = self.user.workspace_set.all().count()

    @property
    def has_plan(self):
        try:
            return CurrentSubscription.objects.get(customer=Customer.objects.get(user=self.user))
        except (Customer.DoesNotExist, CurrentSubscription.DoesNotExist) as e:
            logger.info('User has no plan: %s' % self.user)
            return False

    @property
    def can_create_new_matter(self):
        # if we have disabled the limits then always allow user to create matters
        if self.enabled is False:
            logger.info('BILLING_MATTER_LIMIT is Disabled: %s' % self.user)
            return True
        # allow for excluded users
        if self.user.email in settings.BILLING_MATTER_LIMIT.get('EXCLUDE_EMAILS', ()):
            logger.info('User.email is in BILLING_MATTER_LIMIT.EXCLUDE_EMAILS: %s' % self.user)
            return True
        # user is on a plan
        if self.has_plan is not False:
            logger.info('User has a billing plan: %s' % self.user)
            return True
        # otherwise appliy the logic
        logger.info('BILLING_MATTER_LIMIT.MAX_FREE_MATTERS > User.matters.count for User: %s' % self.user)
        return settings.BILLING_MATTER_LIMIT.get('MAX_FREE_MATTERS') > self.num_matters