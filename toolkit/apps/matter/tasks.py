# -*- coding: utf-8 -*-
from toolkit.celery import app
from toolkit.apps.matter.services import MatterExportService


@app.task
def _export_matter(matter):
    matter_export_service = MatterExportService(matter)
    matter_export_service.process()