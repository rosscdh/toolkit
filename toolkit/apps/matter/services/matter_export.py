# -*- coding: utf-8 -*-
"""
Service to export a matter
(executed files get zipped and mailed to the user)
"""
from django.core import signing
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage

from toolkit.core import _managed_S3BotoStorage
from toolkit.core.services.zip import ZipService
from toolkit.apps.matter.mailers import MatterExportFinishedEmail
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

import os
import datetime
import logging
logger = logging.getLogger('django.request')

from .. import MATTER_EXPORT_DAYS_VALID


class MatterExportService(object):
    """
    Service to export a matter and all of the latest revisions of the documents
    for each of its items; and upload it to s3; as well as send an email with a
    salted tokenized link that will allow the lawyer to download their zip
    """
    def __init__(self, matter, requested_by):
        self._token = None  # very important, reset token
        self.matter = matter
        self.requested_by = requested_by
        self.needed_revisions = []
        self.needed_files = []
        self.created_at = datetime.datetime.utcnow()
        self.download_link = None
        logger.info('Exporting matter: %s' % self.matter)
        # collect the needed revisions and put them in self.needed_files; make sure they exist on local disk
        self.ensure_needed_files_list()

    @property
    def token_data(self):
        # put everything needed to find the file in AWS into the token
        return {'matter_slug': self.matter.slug,
                'user_pk': self.requested_by.pk,
                'created_at': self.created_at.isoformat()}

    @property
    def token(self):
        if self._token is None:
            self._token = signing.dumps(self.token_data, salt=settings.SECRET_KEY)
        return self._token

    def ensure_needed_files_list(self):
        # collects all latest_revisions with the correct state
        for item in self.matter.item_set.all():
            if item.latest_revision and item.latest_revision not in self.needed_revisions:
                self.needed_revisions.append(item.latest_revision)

    def ensure_files_exist_locally(self):
        # make sure the files exist locally
        for needed_revision in self.needed_revisions:
            needed_revision.ensure_file()
            # download latest_revision
            self.needed_files.append({
                'file': needed_revision.get_document(),
                'path_in_zip': "%s/%s/%s/%s" % (
                    self.matter.slug,
                    needed_revision.item.category if needed_revision.item.category else 'no category',
                    needed_revision.item.name,
                    os.path.basename(needed_revision.executed_file.name))
            })

    def get_zip_filename(self, token_data):
        # returns the filename the created .zip should have
        # in in a function to get called from the download-view without instantiating an object
        return 'exported_documents/%s_%s_%s.zip' % \
               (token_data.get('matter_slug'), token_data.get('user_pk'), slugify(token_data.get('created_at')))

    def create_zip(self, filename):
        # zip all needed files to filename
        zip_service = ZipService(filename)
        zip_service.add_file(self.needed_files)
        return zip_service.compress()

    def send_email(self, token):
        # send the token-link to the owning lawyer
        self.download_link = ABSOLUTE_BASE_URL(reverse('matter:download-exported', kwargs={'token': token}))

        m = MatterExportFinishedEmail(
            subject='Your Matter export has completed',
            message='Your matter "%s" has been exported and is ready to be downloaded from: %s' % (self.matter.name, self.download_link),
            recipients=((self.requested_by.get_full_name(), self.requested_by.email), ))
        m.process()

    def conclude(self):
        # record the event
        self.matter.actions.matter_export_finished(user=self.requested_by)
        #
        # Reset Pending Export
        #
        export_info = self.matter.export_info
        download_valid_until = self.created_at + datetime.timedelta(days=MATTER_EXPORT_DAYS_VALID)
        export_info.update({
            'is_pending_export': False,  # reset it
            'last_exported': datetime.datetime.utcnow().isoformat(),
            'last_exported_by': self.requested_by.get_full_name(),
            'download_valid_until': download_valid_until.isoformat(),
            'download_url': self.download_link,
            # leave the request info alone!
        })
        self.matter.export_info = export_info
        self.matter.save(update_fields=['data'])

    def process(self):
        self.ensure_files_exist_locally()

        # zip everything in self.needed_files
        zip_filename = self.get_zip_filename(self.token_data)
        zip_file_path = self.create_zip(zip_filename)

        # upload to AWS as zip_filename
        s3boto_storage = _managed_S3BotoStorage()
        with default_storage.open(zip_file_path) as myfile:
            result = s3boto_storage.save(zip_filename, myfile)

        # send token-link via email
        self.send_email(self.token)
        self.conclude()
