# -*- coding: utf-8 -*-
"""
Service to export a matter
(executed files get zipped and mailed to the user)
"""
import datetime
from django.conf import settings
from django.core import signing
from django.core.urlresolvers import reverse
from toolkit.apps.matter.mailers import MatterExportFinishedEmail
from toolkit.core.services.zip import ZipService


MATTER_EXPORT_DAYS = getattr(settings, 'MATTER_EXPORT_DAYS', 3)


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

    def ensure_list_of_existing_files(self):
        self.ensure_needed_files_list()
        self.ensure_files_exist_locally()
        self.needed_files = self.needed_revisions

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

        # zip everything in self.needed_files
        valid_until = (datetime.datetime.now() + datetime.timedelta(days=MATTER_EXPORT_DAYS)).isoformat()
        zip_filename = '%s_%s_%s' % (self.matter.slug, self.matter.lawyer.pk, valid_until)
        zip_file_path = self.create_zip(zip_filename)


        # upload to AWS as zip_filename

        token = signing.dumps({'matter_slug': self.matter.slug,
                               'user_pk': self.matter.lawyer.pk,
                               'valid_until': valid_until}, salt=settings.SECRET_KEY)

        # send token-link via email
        self.send_email(token)

        # load zip by: signing.loads(get_url_vale, salt=settings.SECRET_KEY)
