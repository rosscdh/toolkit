# -*- coding: UTF-8 -*-
"""
Sort endpoint
To allow for categories and items within the categories to be set

PATCH /matters/:matter_slug/sort
{
    "categories": ["cat 1", "cat 2", "im not a cat, im a dog"],
    ##"items": [2,5,7,1,12,22,4] ## changed to slug to stay in line with standards
    "items": ['fdafdfsdsfdsa', 'fdafdfgrwge24rt32r32', 't42rt32r32fdsfds']
}

As the cats and order represent the state of the project they need to be handled
as a full state; this also makes it simpler for the angular app simply to filter
and generate a set of categories and their order as well as the items in one go
NB! notice that the ALL of the items are sent so it is a GLOBAL sort_order of
items the angular app simply orders the categories and then inserts the items
in the order they appear in
"""
from django.db import transaction
from django.db import IntegrityError

from rulez import registry as rulez_registry

from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.renderers import UnicodeJSONRenderer

from toolkit.apps.workspace.models import Workspace

from .mixins import (MatterMixin,)

from ..serializers import MatterSerializer

import logging
logger = logging.getLogger('django.request')


class MatterSortView(generics.UpdateAPIView,
                     MatterMixin):
    """
    Endpoint to sort categories and items
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    def update(self, request, **kwargs):
        data = request.DATA.copy()

        if all(k in data.keys() for k in ["categories", "items"]) is False:
            raise exceptions.ParseError('request.DATA must be: {"categories": [], "items": []}')

        if all(type(v) is list for v in data.values()) is False:
            raise exceptions.ParseError('categories and items must be of type list {"categories": [], "items": []}')
        #
        # @BUSINESSRULE run this update as an atomic update (transactions)
        #
        try:
            with transaction.atomic():
                # this will override the categories in the order specified
                self.matter.categories = data.get('categories')
                self.matter.save(update_fields=['data'])  # because categories is a derrived value from data
                #
                # @NOTE the data.items are conformative of the item.sort_order
                #
                for sort_order, slug in enumerate(data.get('items')):
                    self.matter.item_set.filter(slug=slug).update(sort_order=sort_order)  # item must exist by this point as we have its id from the rest call

            self.matter.actions.realtime_event(event='update_sort', obj=self.matter, ident=self.matter.slug, from_user=request.user, detail='matter items sort changed')

        except IntegrityError as e:
            logger.critical('transaction.atomic() integrity error: %s' % e)

        return Response(UnicodeJSONRenderer().render(data=data))

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", MatterSortView)
rulez_registry.register("can_edit", MatterSortView)
rulez_registry.register("can_delete", MatterSortView)
