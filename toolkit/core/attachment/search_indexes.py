# -*- coding: utf-8 -*-
from haystack import indexes
from .models import Revision

import logging
logger = logging.getLogger('django.request')


class RevisionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description', null=True)
    url = indexes.CharField(model_attr='get_absolute_url')

    participants = indexes.MultiValueField()

    date_created = indexes.DateTimeField(model_attr='date_created')
    date_modified = indexes.DateTimeField(model_attr='date_modified')

    def get_model(self):
        return Revision

    def prepare_name(self, obj):
        """
        Name is actually the :name - v:slug to allow for nice searching
        """
        return '%s - %s' % (obj.name, obj.slug)

    def prepare_participants(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        #
        # Note! No participants.all() here as item participants are a call to item.matter.particiapnts.all()
        #
        return [participant.pk for participant in obj.item.matter.participants.all()]

    def index_queryset(self, using=None):
        """
        Update index Queryset
        """
        return self.get_model().objects.select_related().filter(is_current=True)
