# -*- coding: UTF-8 -*-
from toolkit.core.mixins.query import IsDeletedQuerySet
from toolkit.core.mixins import IsDeletedManager


class ReviewDocumentManager(IsDeletedManager):
    def get_query_set(self):
        return IsDeletedQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def deleted(self, **kwargs):
        return super(ReviewDocumentManager, self).get_query_set().filter(is_deleted=True, **kwargs)

    def my_as_reviewer(self, user, **kwargs):
        """
        Where I am a reviewer
        pass in matter=matter to filter by matters
        """
        if not user.is_authenticated():
            return self.get_query_set().none()

        return self.get_query_set().filter(reviewers__in=[user], **kwargs)
