# -*- coding: UTF-8 -*-
from django.core.files import File
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


def _download_file(url, obj, obj_fieldname='executed_file'):
    """
    Task to download a file form a url and save it to a model field
    """

    if url not in [None, '']:
        filename = urlparse.urlparse(url).path
        filename_no_ext, ext = os.path.splitext(filename.split('/')[-1])
        filename = '%s%s' % (filename_no_ext, ext)

        #try:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(url).read())
        img_temp.flush()

        # save the downloaded file to the specified model fieldname
        getattr(obj, obj_fieldname).save(filename, File(img_temp))
        obj.save(update_fields=[obj_fieldname])
        # except:
        #     logger.critical('Could not _download_file: %s' % url)
        #     #raise Exception('Filedownload from URL failed.')