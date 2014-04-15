# -*- coding: utf-8 -*-
from toolkit.apps.workspace.models import Workspace


class MatterCloneService(object):
    """
    Service to clone a matter as a new matter
    """
    source_matter = None
    target_matter = None

    def __init__(self, source_matter, target_matter):
        self.source_matter = source_matter
        self.target_matter = target_matter

        assert type(self.source_matter) == Workspace, 'source_matter must be a Workspace type'
        assert self.source_matter.pk not in [None, ''], 'source_matter must have a pk'

        assert type(self.target_matter) == Workspace, 'target_matter must be a Workspace type'
        assert self.target_matter.pk not in [None, ''], 'target_matter must have a pk'

    def process(self):
        for item in self.source_matter.item_set.all():
            item.pk = None  # pk should be regenerated
            item.slug = None  # slug must be unique too
            item.matter = self.target_matter  # set the matter to be the target matter
            item.save()  # save it out
            # this clear must be called after the save as we dont want to clear the source
            # items documents
            if item.revision_set.all().count() > 0:
                item.revision_set.clear()  # clear the connected documents
