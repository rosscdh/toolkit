# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Q


class TaskManager(models.Manager):
    def for_item(self, item):
        """
        Tasks for a specific item
        """
        return self.get_query_set().filter(item=item)

    def for_item_by_user(self, item, user):
        """
        get tasks for a specific item and a specific user
        """
        user_perms = user.matter_permissions(matter=item.matter)

        # filter by item as a requirement
        qs = self.for_item(item=item)

        if user_perms.role == user_perms.ROLES.client:
            #
            # if the user is a client user then they can only see tasks they have created
            # or that have been assigned to them
            #
            qs = qs.filter(Q(assigned_to=user) | Q(created_by=user))


        return qs
