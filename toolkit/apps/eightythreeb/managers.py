# -*- coding: UTF-8 -*-
from django.db import models


class EightyThreeBManager(models.Manager):
    def awaiting_tracking_code(self):
        # exclude users who have not set their password
        return super(EightyThreeBManager, self).get_query_set().filter(status=self.model.STATUS_83b.irs_recieved)