# -*- coding: UTF-8 -*-
from rest_framework import viewsets

from rulez import registry as rulez_registry

from toolkit.apps.sign.models import SignDocument

from ..serializers import SignatureSerializer
from .review import BaseReviewerSignatoryMixin


class SignatureEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = SignDocument
    serializer_class = SignatureSerializer
    lookup_field = 'pk'

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', ]

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", SignatureEndpoint)
rulez_registry.register("can_edit", SignatureEndpoint)
rulez_registry.register("can_delete", SignatureEndpoint)


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
