# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.core import signing
from toolkit.apps.matter.models import ExportedMatter
from toolkit.celery import app
from toolkit.apps.workspace.services.matter_export import MatterExportService
from toolkit.core.services.zip import ZipService
from .mailers import MatterExportFinishedEmail


@app.task
def _export_matter(matter):
    matter_export_service = MatterExportService(matter)
    needed_files = matter_export_service.get_list_of_existing_files()

    # zip collection
    zip_service = ZipService()
    zip_service.add_files(needed_files)
    zip_file_path = zip_service.compress()

    # create token by: token = signing.dumps(expiry_date, salt=settings.SECRET_KEY)
    # load zip by: signing.loads(get_url_vale, salt=settings.SECRET_KEY)

    # upload to AWS
    # create token-link to AWS and save
    # send token-link via email
    token = signing.dumps((datetime.datetime.now() + datetime.timedelta(days=3)).isoformat(), salt=settings.SECRET_KEY)
    exported_matter = ExportedMatter.objects.create(matter=matter, file=zip_file_path, token=token)

    m = MatterExportFinishedEmail(
        subject='Export has finished',
        message='Your matter has been exported and is ready to get downloaded from: %s' % exported_matter.file.url,
        recipients=((matter.lawyer.get_full_name(), matter.lawyer.email)))
    m.process()