# -*- coding: utf-8 -*-
from toolkit.core.attachment.models import RevisionParticipants


class ShareRevisionService(object):
    """
    """
    user, revision, shared_revision_object = None, None, None

    def __init__(self, user, revision):
        self.user = user
        self.revision = revision
        try:
            self.shared_revision_object = user.shared_revision_set.get(user=self.user, revision=self.revision)
        except RevisionParticipants.DoesNotExist:
            self.shared_revision_object = None

    @property
    def is_shared(self):
        return self.shared_revision_object is not None

    def process(self):
        self.shared_revision_object, created = self.user.shared_revision_set.get_or_create(user=self.user,
                                                                                           revision=self.revision)