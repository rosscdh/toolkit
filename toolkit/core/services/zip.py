# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('django.request')


class ZipService(object):
    """
    Service to compress a list of locally saved files
    """
    def __init__(self):
        self.file_list = []

    def add_file(self, one_file):
        self.file_list.append(one_file)

    def add_files(self, multiple_files):
        for one_file in multiple_files:
            self.add_file(one_file)

    def compress(self):
        # do some zipping
        return '/will/get/the/path/to.zip'