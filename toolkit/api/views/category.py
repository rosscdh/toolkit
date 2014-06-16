# -*- coding: UTF-8 -*-
"""
Category and Closing Groups
"""
from rulez import registry as rulez_registry

from rest_framework import generics
from rest_framework.response import Response

from toolkit.apps.workspace.models import Workspace

from .mixins import (MatterMixin,
                     SpecificAttributeMixin,)

from ..serializers import MatterSerializer


class CategoryView(SpecificAttributeMixin,
                   generics.CreateAPIView,
                   generics.RetrieveAPIView,
                   generics.UpdateAPIView,
                   generics.DestroyAPIView,
                   MatterMixin,):
    """
    /matters/:matter_slug/category/:category (GET,POST,DELETE)
        [lawyer] can assign an item to a category

    view/create/delete a specific closing_group
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    specific_attribute = 'categories'

    def retrieve(self, request, **kwargs):
        obj = self.get_object()
        return Response(obj)

    def update(self, request, **kwargs):
        current_category = kwargs.get('category')
        new_category = request.DATA.get('category')

        if new_category != current_category:
            self.matter.item_set.filter(category=current_category).update(category=new_category)
            self.matter.remove_category(value=current_category)
            self.matter.add_category(value=new_category)
            self.matter.save(update_fields=['data'])

        return Response(self.matter.categories)

    def create(self, request, **kwargs):
        self.get_object()

        cats = self.object.add_category(self.kwargs.get('category'))
        self.object.save(update_fields=['data'])

        return Response(cats)

    def delete(self, request, **kwargs):
        cats = self.get_object()
        category = self.kwargs.get('category')

        # try:
        #
        # @BUSINESSRULE at the matter level if we delete a category it will
        # also delete all items below that category
        #
        cats = self.object.remove_category(category, instance=self.object, delete_items_still_using_category=True)
        self.object.save(update_fields=['data'])

        # except Exception as e:
        #     logger.info('Could not delete category: %s due to: %s' % (category, e,))

        return Response(cats)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        self.get_object()  # needed so self.object is set. self.get_object() returns category-list which we can't use here
        return user.matter_permissions(matter=self.object).has_permission(manage_items=True) is True

    def can_delete(self, user):
        self.get_object()  # needed so self.object is set. self.get_object() returns category-list which we can't use here
        return user.matter_permissions(matter=self.object).has_permission(manage_items=True) is True


rulez_registry.register("can_read", CategoryView)
rulez_registry.register("can_edit", CategoryView)
rulez_registry.register("can_delete", CategoryView)
