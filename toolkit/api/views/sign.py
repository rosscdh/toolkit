# -*- coding: UTF-8 -*-
from rest_framework import generics

from .review import BaseReviewerSignatoryMixin


class ItemRevisionSignatoriesView(BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/signers (GET,POST)
        [lawyer,customer] to list and create signers
    """
    pass


class ItemRevisionSignatoryView(BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/signatory/:username (GET,DELETE)
        [lawyer,customer] to show and delete signers
    Get the specified signatory for info purposes
    Is the same functionality as the ItemRevisionReviewerView
    """
    def get_revision_object_set_queryset(self):
        return self.revision.signers
