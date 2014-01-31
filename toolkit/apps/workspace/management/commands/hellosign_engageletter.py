# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

import pprint
PPP = pprint.PrettyPrinter(indent=4)

from tempfile import NamedTemporaryFile

from toolkit.apps.workspace.services import HelloSignService, WordService

from toolkit.apps.engageletter.models import EngagementLetter


class Command(BaseCommand):
    args = '<engageletter slug ...>'
    help = "Test integration with HelloSign"

    service = HelloSignService

    def handle(self, *args, **options):
        try:
            engageletter_slug = args[0]
        except IndexError:
            raise CommandError('You must specify a engageletter slug')

        e = EngagementLetter.objects.get(slug=engageletter_slug)

        invitees = [
            {'name': 'Ross Customer', 'email': 'ross+customer@lawpal.com'},
            {'name': 'Ross Tech Lawyer', 'email': 'ross+lawyer@lawpal.com'}
        ]

        subject = 'Test Signing'
        message = 'This is a test singing please delete'

        doc_service = WordService()
        document = doc_service.generate(html=e.html())

        service = self.service(document=document, invitees=invitees, subject=subject, message=message)
        result = service.send_for_signing(test_mode=1, client_id=settings.HELLOSIGN_CLIENT_ID)
        PPP.pprint(result.json())
        import pdb;pdb.set_trace()
        