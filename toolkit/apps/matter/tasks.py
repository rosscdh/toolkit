# -*- coding: utf-8 -*-
from toolkit.celery import app
from toolkit.apps.matter.services import MatterExportService

import datetime


@app.task
def _export_matter(matter, requested_by):
    #
    # Reset Pending Export
    #
    export_info = matter.export_info
    export_info.update({
        'is_pending_export': True,
        'last_export_requested': datetime.datetime.utcnow().isoformat(),
        'last_export_requested_by': requested_by.get_full_name(),
    })
    matter.save(update_fields=['data'])

    matter_export_service = MatterExportService(matter=matter, requested_by=requested_by)
    matter_export_service.process()