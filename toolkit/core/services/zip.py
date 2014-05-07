# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('django.request')


class ZipService(object):
    """
    Service to compress a list of locally saved files
    """
    def __init__(self, filename):
        self.file_list = []
        self.filename = filename

    def add_file(self, file):
        if hasattr(file, '__iter__'):
            for one_file in file:
                self.file_list.append(file)
        else:
            self.file_list.append(file)

    def compress(self):
        # do some zipping
        return '/will/get/the/path/to.zip'

    def process(self):
        return self.compress()