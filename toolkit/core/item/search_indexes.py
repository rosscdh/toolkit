# -*- coding: utf-8 -*-
import datetime
from haystack import indexes
from .models import Item


class ItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    slug = indexes.CharField(model_attr='slug')
    url = indexes.CharField(model_attr='get_absolute_url')
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description', null=True)
    date_due = indexes.DateTimeField(model_attr='date_due', null=True)
    date_created = indexes.DateTimeField(model_attr='date_created')
    date_modified = indexes.DateTimeField(model_attr='date_modified')

    def get_model(self):
        return Item

    def index_queryset(self, using=None):
        """
        Update index Queryset
        """
        return self.get_model().objects.select_related().all()