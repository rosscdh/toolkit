# -*- coding: UTF-8 -*-
from toolkit.core.mixins.query import IsDeletedQuerySet
from toolkit.core.mixins import IsDeletedManager


class SignDocumentManager(IsDeletedManager):
    def get_query_set(self):
        return IsDeletedQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def deleted(self, **kwargs):
        return super(SignDocumentManager, self).get_query_set().filter(is_deleted=True, **kwargs)

    def my_as_participant(self, user, **kwargs):
        """
        Show my SignDocuments where I am an owner (participant)
        This is useful for seeing a list of sign requests on my matter
        pass in matter=matter to filter by matters
        """
        if not user.is_authenticated():
            return self.get_query_set().none()

        return self.get_query_set().filter(participants__in=[user], **kwargs)

    def my_as_signer(self, user, **kwargs):
        """
        Where I am a signer
        pass in matter=matter to filter by matters
        """
        if not user.is_authenticated():
            return self.get_query_set().none()

        return self.get_query_set().filter(signers__in=[user], **kwargs)
