# -*- coding: UTF-8 -*-
from django.db import models

import datetime


class EightyThreeBManager(models.Manager):
    """
    Default objects manager with helper methods
    """
    def mail_delivery_pending(self):
        return super(EightyThreeBManager, self).get_query_set().filter(status=self.model.STATUS_83b.irs_recieved)

    def incomplete(self):
        return super(EightyThreeBManager, self).get_query_set() \
                                                .exclude(status=self.model.STATUS_83b.complete) \
                                                .filter(filing_date__gte=datetime.date.today())
