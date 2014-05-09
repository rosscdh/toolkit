# -*- coding: utf-8 -*-
import logging

from django.core.files.storage import default_storage

from toolkit.core import _managed_S3BotoStorage


logger = logging.getLogger('django.request')


class FileExistsLocallyMixin(object):
    """
    Mixin to ensure we have the file available on the local filesystem, this is
    important as in order to send documents for review at crocdoc and or for
    signing at hellosign; the document must be available locally
    @TODO make this asynchronous
    """
    def get_document(self):
        raise NotImplementedError

    def get_document_name(self):
        return self.get_document().name

    def ensure_file(self):
        """
        initially this will be called in the view; but may cause render slowness
        in the case of larger files that are not present on the local machine
        eventually should have django-storages syncing all the filestores with
        these files
        """
        if self.file_exists_locally is False:
            # Download the file
            #
            file_name = self.get_document_name()
            logger.info('File.DoesNotExistLocally: %s downloading' % file_name)
            return self.download_file(file_name=file_name)
        return False

    @property
    def file_exists_locally(self):
        """
        Used to determine if we should download the file locally
        """
        try:
            return default_storage.exists(self.get_document())
        except Exception as e:
            logger.error('File does not exist locally: %s raised exception %s' % (self.get_document(), e))
        return False

    def read_local_file(self):
        if self.file_exists_locally is True:
            return default_storage.open(self.get_document()).read()
        return False

    def download_file(self, file_name):
        """
        Its necessary to download the file from s3 locally as we have restrictive s3
        permissions (adds time but necessary for security)
        """
        b = _managed_S3BotoStorage()

        if b.exists(file_name) is False:
            msg = 'file does not exist on s3: %s' % file_name
            logger.critical(msg)
            raise Exception(msg)

        else:
            #
            # download from s3 and save the file locally
            #
            file_object = b._open(file_name)
            logger.info('Downloading file from s3: %s' % file_name)
            return default_storage.save(file_name, file_object)
