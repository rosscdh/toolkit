# -*- coding: utf-8 -*-
"""
HTML to PDF Conversion Services
"""
from django.conf import settings

import os
import json
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

    def pdf(self, template_name, file_object):
        filename = os.path.basename(template_name)

        payload = {"html": self.html, "filename": filename}
        headers = {'content-type': 'application/json'}

        r = self.service.post(self.PDFKIT_SERVICE_URI, data=json.dumps(payload), headers=headers)
        logger.info('Send HTML to PDF conversion request')

        file_object.write(r.content)
        return file_object


class PDFKitService(PDFKitRubyService):
    """
    Generic Accessor class imported by the system
    needs to extend the class we eventually decide to
    """
    pass
