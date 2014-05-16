# -*- coding: utf-8 -*-
from toolkit.celery import app
from toolkit.apps.matter.services import MatterExportService

import datetime


@app.task
def _export_matter(matter, requested_by):
    matter_export_service = MatterExportService(matter=matter, requested_by=requested_by)
    matter_export_service.process()