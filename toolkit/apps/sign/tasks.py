# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from hellosign.hellosign import HelloSignFinalCopy

from toolkit.celery import app

import logging
import datetime
logger = logging.getLogger('django.request')


@app.task
def _download_signing_complete_document(hellosign_request, **kwargs):
    final_copy_uri = hellosign_request.data.get('signature_request', {}).get('final_copy_uri', None)

    if final_copy_uri is None:
        logger.critical(u'No final_copy_uri was provided by Hellosign for: %s' % hellosign_request)

    else:
        # download the document from HS
        service = HelloSignFinalCopy()

        # get the doc revision
        document_revision = hellosign_request.source_object.document

        # get the file
        try:
            final_copy_contents = service.download(signature_id=hellosign_request.signature_request_id,
                                                   auth=settings.HELLOSIGN_AUTHENTICATION)
        except service.DownloadFinalCopyException as e:

            logger.critical(u'Could not download Executd HelloSign Document: %s due to: %s' % (document_revision, e))

        else:
            # update the doc revision object
            doc_name = 'executed-%s' % document_revision.name
            size = len(final_copy_contents)

            logger.debug(u'doc_name: %s (%s)' % (doc_name, size))
            content_object = ContentFile(final_copy_contents)
            # save the file and via the default storage for the field
            document_revision.executed_file.save(doc_name, content_object)
            # save the file locally
            default_storage.save(document_revision.executed_file.name, content_object)

            data = document_revision.data
            date_executed = datetime.datetime.utcnow()
            data.update({
                'executed': {
                    'date_executed': date_executed
                }
            })
            # update the data
            document_revision.data = data
            # set is_executed to true
            document_revision.is_executed = True
            document_revision.save(update_fields=['executed_file', 'is_executed', 'data'])

            logger.info('Executed: %s on %s' % (document_revision, date_executed))