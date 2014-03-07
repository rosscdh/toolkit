# -*- coding: UTF-8 -*-
"""
Matter resolver Mixins
"""
from django.shortcuts import get_object_or_404

from rest_framework import generics

from toolkit.core.item.models import Item
from toolkit.apps.workspace.models import Workspace


class MatterMixin(generics.GenericAPIView):
    """
    Get the matter from the url slug :matter_slug
    """
    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        return super(MatterMixin, self).initialize_request(request, *args, **kwargs)


class MatterItemsQuerySetMixin(MatterMixin):
    """
    Mixin to filter the Items objects by their matter via the url :matter_slug
    """
    def get_queryset(self):
        return Item.objects.filter(matter=self.matter)


class SpecificAttributeMixin(object):
    """
    mixin to allow use of specific attribute mixin
    """
    specific_attribute = None

    def __init__(self, *args, **kwargs):
        if self.specific_attribute is None:
            raise Exception('You must define a self.specific_attribute attrib that exists on the object')

        super(SpecificAttributeMixin, self).__init__(*args, **kwargs)

    def get_object(self):
        self.object = super(SpecificAttributeMixin, self).get_object()
        return getattr(self.object, self.specific_attribute, None)
