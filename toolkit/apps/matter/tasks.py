# -*- coding: utf-8 -*-
from django.core import management

from toolkit.celery import app
from toolkit.apps.matter.services import MatterExportService

import datetime


@app.task
def _export_matter(matter, requested_by, provider=None):
    if provider is None:
        matter_export_service = MatterExportService(matter=matter, requested_by=requested_by)
        matter_export_service.process()

    if provider == 'box':
        management.call_command('sync_box', matter.slug, usernames=requested_by.username)

    if provider == 'dropbox-oauth2':
        management.call_command('sync_dropbox', matter.slug, usernames=requested_by.username)