# -*- coding: utf-8 -*-
from django.db.models import Q
from toolkit.apps.workspace.models import ROLES
from toolkit.core.mixins import IsDeletedManager


class RevisionManager(IsDeletedManager):
    def get_query_set(self):
        qs = super(RevisionManager, self).get_query_set()
        return qs.select_related('matter', 'item', 'uploaded_by')

    def current(self):
        return self.filter(is_current=True)

    def visible(self, user, matter):
        # perhaps the self.item.responsible_party needs to be used?
        qs = self.get_query_set()
        if user.matter_permissions(matter).role == ROLES.client \
                or user.matter_permissions(matter).has_permission(manage_items=False):
            # if I am client or I do not have manage_items-permissions, my revisions are filtered:
            # just show those I uploaded or I am reviewing
            qs = qs.filter(Q(reviewers=user) | Q(uploaded_by=user))
        return qs