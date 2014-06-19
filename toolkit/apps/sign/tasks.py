# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from hellosign.hellosign import HelloSignFinalCopy
from hellosign.hellosign import HelloSignSignature

from toolkit.celery import app

import os
import logging
import datetime
logger = logging.getLogger('django.request')


def _hellosign_signature_subject_and_message(request_id):
    """
    We need to query the HS api to get the subject and message for the signature
    as they do not currently send it back in the javascript callback; have raised
    and they are assessing impact.
    """
    auth = getattr(settings, 'HELLOSIGN_AUTHENTICATION', None)
    client = HelloSignSignature()
    resp = client.detail(auth=auth, signature_request_id=request_id)
    # parse json
    resp_json = resp.json().get('signature_request',{})
    # get needed info
    subject = resp_json.get('subject', None)
    message = resp_json.get('message', None)
    # return tuple
    logger.info(u'Got subject, message from HS request_id: %s' % request_id)
    return subject, message


@app.task
def _send_for_signing(from_user, sign_object, signature_request_id, **kwargs):
    """
    Task takes a request_id and sends it for signing and then sends the
    invite email to appropriate users
    """
    subject = kwargs.get('subject', None)
    message = kwargs.get('message', None)

    if subject is None and message is None:
        logger.info(u'subject, message not passed into task HS request_id: %s' % signature_request_id)
        subject, message = _hellosign_signature_subject_and_message(request_id=signature_request_id)

    resp = sign_object.send_for_signing(signature_request_id=signature_request_id)

    if resp.get('date_sent', None) is None:
        logger.error(u'Sent %s for signing but got unexpected response (date_sent not present): %s' % (signature_request_id, resp))

    else:
        logger.info(u'Sent %s for signing and got response' % signature_request_id)
        # Recalculate the percentage
        sign_object.document.item.recalculate_signing_percentage_complete()

        sign_object.send_invite_email(from_user=from_user,
                                      subject=subject,
                                      message=message)


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

            logger.critical(u'Could not download Executed HelloSign Document: %s due to: %s' % (document_revision, e))

        else:
            # update the doc revision object
            doc_name = 'executed-%s' % document_revision.name
            size = len(final_copy_contents)

            logger.debug(u'doc_name: %s (%s)' % (doc_name, size))
            content_object = ContentFile(final_copy_contents)
            # save the file and via the default storage for the field
            document_revision.executed_file.save(doc_name, content_object)

            # remove extension
            split_file_name = os.path.split(document_revision.executed_file.name)[-1]
            filename_no_ext, ext = os.path.splitext(split_file_name)
            ext = ext[1:]  # remove the . in the .pdf which comes in as ext

            # save the file locally
            default_storage.save('%s.pdf' % filename_no_ext, content_object)  # always pdfs from HS

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

            # set the item to complete
            item = document_revision.item
            item.is_complete = True
            item.save(update_fields=['is_complete'])

            logger.info('Executed: %s on %s' % (document_revision, date_executed))