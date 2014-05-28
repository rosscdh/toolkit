# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from hellosign.hellosign import HelloSignFinalCopy

from toolkit.celery import app
from toolkit.api.serializers import RevisionSerializer

import logging
logger = logging.getLogger('django.request')


@app.task
def _download_signing_complete_document(hellosign_request, **kwargs):
    document_revision = hellosign_request.source_object.document

    final_copy_uri = hellosign_request.data.get('signature_request', {}).get('final_copy_uri', None)

    if final_copy_uri is None:
        logger.critical(u'No final_copy_uri was provided by Hellosign for: %s' % hellosign_request)

    else:
        # download the document from HS
        service = HelloSignFinalCopy()
        resp = service.download(signature_id=hellosign_request.signature_request_id,
                                auth=settings.HELLOSIGN_AUTHENTICATION)

        data = {
            'executed_file': SimpleUploadedFile(document_revision.executed_file.name, resp.content, content_type='application/pdf')
        }
        import pdb;pdb.set_trace()
        file_data = {
            'executed_file': SimpleUploadedFile(document_revision.executed_file.name, resp.content, content_type='application/pdf')
        }

        serializer = RevisionSerializer(document_revision, data=data, partial=True)