# -*- coding: UTF-8 -*-
from django.db import models

from toolkit.core.mixins.query import IsDeletedQuerySet
from toolkit.core.mixins import IsDeletedManager

import datetime


class EightyThreeBManager(IsDeletedManager):
    """
    Default objects manager with helper methods
    """
    def mail_delivery_pending(self):
        return super(EightyThreeBManager, self).get_query_set().filter(status=self.model.STATUS.irs_recieved) \
                                                               .filter(filing_date__gte=datetime.date.today())

    def incomplete(self):
        """
        @Business rule
        exclude completed as well as those in the waiting for usps delivery as it is out of the users hands at this point
        """
        return super(EightyThreeBManager, self).get_query_set() \
                                                .exclude(status__in=self.model.INCOMPLETE_EXCLUDED_STATUS) \
                                                .filter(filing_date__gte=datetime.date.today())


class AttachmentManger(IsDeletedManager):
    """
    Manager for 83b attachments
    """
    pass
