# -*- coding: utf-8 -*-
from toolkit.apps.workspace.models import Workspace

import datetime
import logging
logger = logging.getLogger('django.request')


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
        num_items = self.source_matter.item_set.all().count()

        logger.info('Cloning Matter source: %s target: %s num_items: %d' % (self.source_matter, self.target_matter, num_items) )

        for item in self.source_matter.item_set.all():

            item.pk = None  # pk should be regenerated
            item.slug = None  # slug must be unique too
            item.matter = self.target_matter  # set the matter to be the target matter
            item.latest_revision = None  # remove any connected revisions
            item.save()  # save it out

        self.target_matter.data['cloned'] = {
            'date_cloned': datetime.datetime.utcnow(),
            'num_items': num_items,
        }
        self.target_matter.save(update_fields=['data'])
