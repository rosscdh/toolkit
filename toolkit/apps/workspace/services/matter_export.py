# -*- coding: utf-8 -*-
"""
Service to export a matter
(executed files get zipped and mailed to the user)
"""


class MatterExportService(object):
    def __init__(self, matter):
        self.matter = matter
        self.needed_revisions = []

    def ensure_needed_files_list(self):  # TODO: perhaps rename to list_executed_files (depending on which files we collect)
        for item in self.matter.item_set.all():  # all items must be completed, otherwise the button wasn't shown
            if item.latest_revision:
                self.needed_revisions.append(item.latest_revision)

    def ensure_files_exist_locally(self):
        for needed_revision in self.needed_revisions:
            # download latest_revision
            downloaded_file = needed_revision.ensure_file()

    def get_list_of_existing_files(self):
        self.ensure_needed_files_list()
        self.ensure_files_exist_locally()
        return self.needed_revisions