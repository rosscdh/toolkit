# -*- coding: utf-8 -*-
"""
Service to export a matter
(executed files get zipped and mailed to the user)
"""
import datetime
from django.conf import settings
from django.core import signing
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from storages.backends.s3boto import S3BotoStorage
from toolkit.apps.matter.mailers import MatterExportFinishedEmail
from toolkit.core.services.zip import ZipService


MATTER_EXPORT_DAYS = getattr(settings, 'MATTER_EXPORT_DAYS', 3)


class MatterExportService(object):
    def __init__(self, matter):
        self.matter = matter
        self.needed_revisions = []
        self.needed_files = []

    def ensure_needed_files_list(self):  # TODO: perhaps rename to list_executed_files (depending on which files we collect)
        for item in self.matter.item_set.all():  # all items must be completed, otherwise the button wasn't shown
            if item.latest_revision:
                self.needed_revisions.append(item.latest_revision)

    def ensure_files_exist_locally(self):
        for needed_revision in self.needed_revisions:
            # download latest_revision
            needed_revision.ensure_file()
            self.needed_files.append(needed_revision.get_document())

    def ensure_list_of_existing_files(self):
        self.ensure_needed_files_list()
        self.ensure_files_exist_locally()

    def get_zip_filename(self, token_data):
        # in in a function to get called from the download-view without instantiating an object
        return '%s_%s_%s' % (token_data.get('matter_slug'), token_data.get('user_pk'), token_data.get('valid_until'))

    def create_zip(self, filename):
        # zip collection
        zip_service = ZipService(filename)
        zip_service.add_file(self.needed_files)
        return zip_service.compress()

    def send_email(self, token):
        # download_link = reverse('list')
        # download_link = reverse('download-exported', args=(token, ))

        download_link = 'asdf'

        m = MatterExportFinishedEmail(
            subject='Export has finished',
            message='Your matter "{{ matter.name }}" has been exported and is ready to be downloaded from: %s' % download_link,
            recipients=((self.matter.lawyer.get_full_name(), self.matter.lawyer.email)))
        m.process()

    def process(self):
        # collect the needed revisions and put them in self.needed_files
        self.ensure_list_of_existing_files()

        # put everything needed to find the file into the token
        valid_until = (datetime.datetime.now() + datetime.timedelta(days=MATTER_EXPORT_DAYS)).isoformat()
        token_data = {'matter_slug': self.matter.slug,
                      'user_pk': self.matter.lawyer.pk,
                      'valid_until': valid_until}

        token = signing.dumps(token_data, salt=settings.SECRET_KEY)

        # zip everything in self.needed_files
        zip_filename = self.get_zip_filename(token_data)
        zip_file_path = self.create_zip(zip_filename)

        # upload to AWS as zip_filename
        s3boto_storage = S3BotoStorage()
        with default_storage.open(zip_file_path) as myfile:
            result = s3boto_storage.save('exported_matters/%s.zip' % zip_filename, myfile)  # seems to need open file instead of path

        # send token-link via email
        self.send_email(token)