# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models.query import QuerySet

import datetime


class isDeletedQuerySet(QuerySet):
    """
    Mixin to override the Queryset.delete() functionality of a manager
    """
    def delete(self, *args, **kwargs):
        if 'is_deleted' in self.model._meta.get_all_field_names():
            self.update(is_deleted=True)
        else:
            super(isDeletedQuerySet, self).delete()


class EightyThreeBManager(models.Manager):
    """
    Default objects manager with helper methods
    """
    def mail_delivery_pending(self):
        return super(EightyThreeBManager, self).get_query_set().filter(status=self.model.STATUS_83b.irs_recieved)

    def incomplete(self):
        """
        @Business rule
        exclude completed as well as those in the waiting for usps delivery as it is out of the users hands at this point
        """
        return super(EightyThreeBManager, self).get_query_set() \
                                                .exclude(status__in=[self.model.STATUS_83b.complete, self.model.STATUS_83b.irs_recieved])
                                                #.filter(filing_date__gte=datetime.date.today())


class AttachmentManger(models.Manager):
    """
    Manager for 83b attachments
    """
    def get_query_set(self):
        return isDeletedQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def deleted(self):
        return super(AttachmentManger, self).get_query_set().filter(is_deleted=True)