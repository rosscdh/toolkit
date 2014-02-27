# -*- coding: utf-8 -*-
"""
HTML to PDF Conversion Services
"""
from django.conf import settings
from django.core.files.base import ContentFile

from tempfile import gettempdir

import os
import json
import uuid
import requests

from . import logger


class BasePdfService(object):
    """
    Base class for converting provided HTML to a pdf or png
    """
    options = None

    def __init__(self, html):
        self.html = html
        self.service = self.get_service()

    def get_service(self):
        raise NotImplementedError

    def pdf(self, template_name, context, file_object):
        raise NotImplementedError


class PDFKitRubyService(BasePdfService):
    """
    Send requests to local PDFKit service that formats HTML nicely
    """
    PDFKIT_SERVICE_URI = getattr(settings, 'PDFKIT_SERVICE_URI', 'http://localhost:9292/v1/html/to/pdf')

    def get_service(self):
        return requests

    def pdf(self, file_object=None, template_name=None):
        file_object = open('%s%s' % (gettempdir(), '%s.pdf' % uuid.uuid4()), 'w+') if file_object is None else file_object
        filename =  os.path.basename(file_object.name) if template_name is None else os.path.basename(template_name)

        payload = {
            "html": self.html,
            #"footer": '',
            "filename": filename
        }
        headers = {'content-type': 'application/json'}
        payload_json = json.dumps(payload)

        logger.info('Send HTML to PDF conversion request: %s' % payload_json)
        r = self.service.post(self.PDFKIT_SERVICE_URI, data=payload_json, headers=headers)

        logger.info('Got status_code %s for request' % r.status_code)

        if r.status_code in [201]:
            logger.info('Got status_code %s for request' % r.status_code)
            file_object.write(r.content)
            file_object.close()

        return file_object


class PDFKitService(PDFKitRubyService):
    """
    Generic Accessor class imported by the system
    needs to extend the class we eventually decide to
    """
    pass
