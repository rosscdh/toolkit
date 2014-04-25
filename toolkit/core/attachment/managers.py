# -*- coding: utf-8 -*-
from toolkit.core.mixins import IsDeletedManager


class RevisionManager(IsDeletedManager):
    def get_query_set(self):
        qs = super(RevisionManager, self).get_query_set()
        return qs.select_related('matter', 'item', 'uploaded_by')

    def current(self):
        return self.filter(is_current=True)
