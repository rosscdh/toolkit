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
            # import pdb;pdb.set_trace()
            qs = qs.filter(
                # (Q(item__is_requested=True) & Q(item__responsible_party=user)) |  # file should be uploaded by user
                # if item was is_requested=True and a revision is saved, it is not is_requested any more! -> check uploaded_by

                Q(signers=user) |  # file should be signed by user
                Q(reviewers=user) |  # file should be reviewed by user
                Q(uploaded_by=user)  # file was uploaded by user
            )
            qs = qs.filter()
        return qs