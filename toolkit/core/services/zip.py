# -*- coding: utf-8 -*-
import logging
import os
from zipfile import ZipFile
from django.core.files.storage import default_storage

logger = logging.getLogger('django.request')


class ZipService(object):
    """
    Service to compress a list of locally saved files
    """
    def __init__(self, filename):
        self.file_list = []
        self.filename = filename
        self.targetfolder = "%s/exported_matters/" % default_storage.location
        self.ensure_targetfolder()

    def ensure_targetfolder(self):
        d = os.path.dirname(self.targetfolder)
        if not os.path.exists(d):
            os.makedirs(d)

    def add_file(self, file):
        if hasattr(file, '__iter__'):
            for one_file in file:
                self.file_list.append(one_file)
        else:
            self.file_list.append(file)

    def compress(self):
        # do some zipping
        target_path = "%s/exported_matters/%s.zip" % (default_storage.location, self.filename)
        with ZipFile(target_path, 'w') as myzip:
            for file_to_add in self.file_list:
                myzip.write('%s/%s' % (default_storage.location, file_to_add.name), arcname=file_to_add.name)
                # TODO: think of better structure within the zip. perhaps add a 'target_filename' to add_file.
        return target_path

    def process(self):
        return self.compress()