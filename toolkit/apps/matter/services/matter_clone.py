# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile

from toolkit.apps.workspace.models import Workspace

import os
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

    def process_item(self, item):
        item.pk = None  # pk should be regenerated
        item.slug = None  # slug must be unique too
        item.matter = self.target_matter  # set the matter to be the target matter
        item.latest_revision = None  # remove any connected revisions
        item.is_requested = False
        item.is_complete = False
        item.is_final = False
        item.date_due = None
        item.status = item.ITEM_STATUS.new
        item.data = {}  # reset all status etc
        item.save()
        return item

    def update_matter_data(self, matter, **kwargs):
        matter.data['cloned'] = {
            'date_cloned': datetime.datetime.utcnow(),
            'num_items': kwargs.get('num_items'),
        }
        return matter


    def process(self):
        num_items = self.source_matter.item_set.all().count()

        logger.info('Cloning Matter source: %s target: %s num_items: %d' % (self.source_matter, self.target_matter, num_items) )

        for item in self.source_matter.item_set.all():
            self.process_item(item=item)

        # Bulk create the items
        # cant bulk create as we need save to be called
        #
        #item.__class__.objects.bulk_create(bulk_create_items)

        # clone the categories via the mixin attribs to preserve order
        self.target_matter.categories = self.source_matter.categories
        self.target_matter = self.update_matter_data(matter=self.target_matter, num_items=num_items)
        self.target_matter.save(update_fields=['data'])


class DemoMatterCloneService(MatterCloneService):
    """
    Service used to setup a demo matter when a new user is created
    """
    def process_item(self, item):
        """
        For the demo we also want to copy the revisions and associated documents
        """
        revisions = item.revision_set.all()
        item = super(DemoMatterCloneService, self).process_item(item=item)

        #
        # Now clone the revisions and copy their documents
        #
        for rev in revisions:

            rev.pk = None  # invalidate its pk
            rev.item = item # the new created item

            # give the new file a name prefixed with the matter.pk
            # NEW_EXECUTED_PATH = '%s/%s-%s' % (os.path.dirname(rev.executed_file.name), item.matter.pk, os.path.basename(rev.executed_file.name))

            try:
                #
                # @TODO must be a simpler way
                #
                # with open(NEW_EXECUTED_PATH, 'w') as executed_file:
                #     # read the contents of the file into the new local_file
                #     executed_file.write(rev.executed_file.read())

                new_executed_file = ContentFile(rev.executed_file.read())
                new_executed_file.name = rev.executed_file.name
                rev.executed_file = new_executed_file

            except IOError:
                logger.critical('DemoMatterCloneService: executed_file: %s does not exist' % rev.executed_file.name)

            rev.save()

    def update_matter_data(self, matter, **kwargs):
        """
        set is_demo = True so we can show the intro js tutorial on it
        """
        matter = super(DemoMatterCloneService, self).update_matter_data(matter=matter, **kwargs)
        matter.data['is_demo'] = True
        return matter
