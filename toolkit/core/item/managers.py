# -*- coding: UTF-8 -*-
from toolkit.core.mixins import IsDeletedManager


class ItemManager(IsDeletedManager):
    """
    Provide filters for the various item status
    """
    def awaiting_documents(self, **kwargs):
        return super(ItemManager, self).get_query_set().filter(status=self.model.ITEM_STATUS.awaiting_document, **kwargs)