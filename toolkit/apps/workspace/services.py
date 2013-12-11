# -*- coding: utf-8 -*-
"""
Services to the workspace
"""
from django.conf import settings
from django.contrib.auth.models import User

from toolkit.apps.default import _get_unique_username

from django_xhtml2pdf.utils import generate_pdf

import requests
import pdfkit
import os
import json
import logging
LOGGER = logging.getLogger('django.request')
PDFKIT_SERVICE_URI = getattr(settings, 'PDFKIT_SERVICE_URI', 'http://localhost:9292/v1/html/to/pdf')


class EnsureCustomerService(object):
    """
    Service to get or create a Customer User
    """
    def __init__(self, email, full_name=None):
        self.email = email
        self.full_name = full_name
        self.is_new, self.user, self.profile = (None, None, None)

    def process(self):
        if self.email is None:
            LOGGER.error('Email is None, cant create user')
        else:
            self.is_new, self.user, self.profile = self.get_user(email=self.email)

    def get_user(self, email, **kwargs):

        try:
            user = User.objects.get(email=email, **kwargs)
            is_new = False

        except User.DoesNotExist:
            user = User.objects.create(username=_get_unique_username(username=email.split('@')[0]), email=email, **kwargs)
            is_new = True

        profile = user.profile

        if is_new is True or 'user_class' not in profile.data:
            LOGGER.info('Is a new User')
            profile.data['user_class'] = 'customer'
            profile.save(update_fields=['data'])

        # setup the name of the user
        # and set it if they exist but have no name
        if self.full_name is not None:
            LOGGER.info('Full Name was provided')
            # extract the first and last name
            names = self.full_name.split(' ')
            update_fields = []

            if user.first_name in [None, '']:
                user.first_name = names[0]
                update_fields.append('first_name')
                LOGGER.info('Updating first_name')

            if user.last_name in [None, '']:
                user.last_name = ' '.join(names[1:])
                update_fields.append('last_name')
                LOGGER.info('Updating last_name')

            # save the user model
            user.save(update_fields=update_fields)

        return is_new, user, profile


class HTMLtoPDForPNGService(object):
    """
    Convert provided HTML to a pdf or png
    """
    options = None

    def __init__(self, html):
        self.html = html
        self.service = self.get_service()

    def get_service(self):
        return generate_pdf

    def pdf(self, template_name, context, file_object=None):
        # Write PDF to file
        return self.service(template_name, file_object=file_object, context=context)


class PDFKitLocalService(HTMLtoPDForPNGService):
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }

    def get_service(self):
        return pdfkit

    def pdf(self, template_name, file_object):
        filename = os.path.basename(template_name)

        r = self.service.from_string(self.html, False, options=self.options)

        file_object.write(r)
        return file_object


class PDFKitRubyService(HTMLtoPDForPNGService):
    """
    Send requests to local PDFKit service that formats HTML nicely
    """
    def get_service(self):
        return requests

    def pdf(self, template_name, file_object):
        filename = os.path.basename(template_name)

        payload = {"html": self.html, "filename": template_name}
        headers = {'content-type': 'application/json'}

        r = self.service.post(PDFKIT_SERVICE_URI, data=json.dumps(payload), headers=headers)

        file_object.write(r.content)
        return file_object


class PDFKitService(PDFKitRubyService):
    pass
