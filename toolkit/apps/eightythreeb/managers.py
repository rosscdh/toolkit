# -*- coding: UTF-8 -*-
from django.db import models


class EightyThreeBManager(models.Manager):
    def mail_delivery_pending(self):
        # exclude users who have not set their password
        return super(EightyThreeBManager, self).get_query_set().filter(status=self.model.STATUS_83b.irs_recieved)