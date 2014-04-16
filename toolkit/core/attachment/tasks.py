# -*- coding: UTF-8 -*-
from django.core.files import File
from django.core.validators import URLValidator
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile

# urlparse compat import (Required because it changed in python 3.x)
try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse

import os
import urllib2
import logging
logger = logging.getLogger('django.request')


def _download_file(url, obj, obj_fieldname='executed_file', filename=None, update_obj=True):
    """
    Task to download a file form a url and save it to a model field
    """

    if url not in [None, '']:

        # Validate the url
        URLValidator(url)

        if filename is None:
            filename = urlparse.urlparse(url).path

        filename_no_ext, ext = os.path.splitext(filename.split('/')[-1])
        #
        # @BUSINESSRULE must have a file .suffix
        #
        if ext is None:
            raise Exception('Cannot download a file with no filename.extension: %s' % url)

        filename = '%s%s' % (filename_no_ext, ext)

        #try:
        img_temp = NamedTemporaryFile(delete=True, suffix=ext)
        img_temp.write(urllib2.urlopen(url).read())
        img_temp.flush()

        #
        # SAVE THE FILE LOCALLY
        #
        # use the upload_to function to name and place the file appropriately
        filename = obj._meta.get_field(obj_fieldname).upload_to(instance=obj, filename=filename)
        file_object = File(img_temp)
        # return both the filename and the file_object for saving to the model
        return (default_storage.save(filename, file_object), file_object,)