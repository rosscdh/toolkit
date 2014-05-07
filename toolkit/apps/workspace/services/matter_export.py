# -*- coding: utf-8 -*-
"""
Service to export a matter
(executed files get zipped and mailed to the user)
"""
import datetime
import os
from django.conf import settings
from django.core import signing
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from storages.backends.s3boto import S3BotoStorage
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.apps.matter.mailers import MatterExportFinishedEmail
from toolkit.core.services.zip import ZipService


MATTER_EXPORT_DAYS_VALID = getattr(settings, 'MATTER_EXPORT_DAYS_VALID', 3)


class MatterExportService(object):
    def __init__(self, matter):
        self.matter = matter
        self.needed_revisions = []
        self.needed_files = []

    def get_zip_filename(self, token_data):
        # returns the filename the created .zip should have
        # in in a function to get called from the download-view without instantiating an object
        return 'exported_documents/%s_%s_%s.zip' % \
               (token_data.get('matter_slug'), token_data.get('user_pk'), token_data.get('valid_until'))

    def ensure_needed_files_list(self):  # TODO: perhaps rename to list_executed_files (depending on which files we collect)
        # collects all latest_revisions with the correct state
        for item in self.matter.item_set.all():
            if item.latest_revision:
                self.needed_revisions.append(item.latest_revision)

    def ensure_files_exist_locally(self):
        # make sure the files exist locally
        for needed_revision in self.needed_revisions:
            # download latest_revision
            needed_revision.ensure_file()
            self.needed_files.append({
                'file': needed_revision.get_document(),
                'path_in_zip': "%s/%s/%s" % (needed_revision.item.category.slug if needed_revision.item.category else None,
                                             needed_revision.item.name,
                                             os.path.basename(needed_revision.executed_file.name))
            })

    def create_zip(self, filename):
        # zip all needed files to filename
        zip_service = ZipService(filename)
        zip_service.add_file(self.needed_files)
        return zip_service.compress()

    def send_email(self, token):
        # send the token-link to the owning lawyer
        download_link = ABSOLUTE_BASE_URL(reverse('matter:download-exported', kwargs={'token': token}))

        m = MatterExportFinishedEmail(
            subject='Export has finished',
            message='Your matter "%s" has been exported and is ready to be downloaded from: %s' % (self.matter.name, download_link),
            recipients=((self.matter.lawyer.get_full_name(), self.matter.lawyer.email)))
        m.process()

    def process(self):
        # collect the needed revisions and put them in self.needed_files; make sure they exist on local disk
        self.ensure_needed_files_list()
        self.ensure_files_exist_locally()

        # put everything needed to find the file in AWS into the token
        valid_until = (datetime.datetime.now() + datetime.timedelta(days=MATTER_EXPORT_DAYS_VALID)).isoformat()
        token_data = {'matter_slug': self.matter.slug,
                      'user_pk': self.matter.lawyer.pk,
                      'valid_until': valid_until}

        # zip everything in self.needed_files
        zip_filename = self.get_zip_filename(token_data)
        zip_file_path = self.create_zip(zip_filename)

        # upload to AWS as zip_filename
        s3boto_storage = S3BotoStorage()
        with default_storage.open(zip_file_path) as myfile:
            result = s3boto_storage.save(zip_filename, myfile)

        # send token-link via email
        token = signing.dumps(token_data, salt=settings.SECRET_KEY)
        self.send_email(token)