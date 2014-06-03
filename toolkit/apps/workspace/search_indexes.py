# -*- coding: utf-8 -*-
import datetime
from haystack import indexes
from .models import Workspace


class WorkspaceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description', null=True)
    url = indexes.CharField(model_attr='get_absolute_url')

    participants = indexes.MultiValueField()

    date_created = indexes.DateTimeField(model_attr='date_created')
    date_modified = indexes.DateTimeField(model_attr='date_modified')

    def get_model(self):
        return Workspace

    def prepare_participants(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [participant.pk for participant in obj.participants.all()]

    def index_queryset(self, using=None):
        """
        Update index Queryset
        """
        return self.get_model().objects.select_related().all()