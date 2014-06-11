# -*- coding: utf-8 -*-
from toolkit.celery import app

from .services import CrocodocLoaderService

import requests
import logging
logger = logging.getLogger('django.request')


@app.task(name='review.uploader.crocodoc_upload_task')
def crocodoc_upload_task(user, revision):
    """
    Async Celery task to start the upload of the file to crocodoc, as crocodoc is
    hell slow... and our users are impatient as they should be.
    """
    #
    # Get all the documents and start their uplaod
    #
    for reviewdocument in revision.reviewdocument_set.all():
        logger.info('Upload of document for review %s for %s' % (revision, user))
        # get service
        async_uploader_service = CrocodocLoaderService(user=user, reviewdocument=reviewdocument)
        # ensure the file is available locally
        async_uploader_service.ensure_local_file()
        # get the file 
        crocodoc_view_url = async_uploader_service.process().get('crocodoc_view_url', None)

        if crocodoc_view_url is not None:
            r = requests.get(crocodoc_view_url)
            if r.status_code in [200]:
                logger.info('[SUCCESS] Upload of document comment %s for %s' % (revision, user))
            else:
                logger.error('[ERROR] Error in upload of document comment %s for %s' % (revision, user))