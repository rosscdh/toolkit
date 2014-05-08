# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from hellosign import HelloSignUnclaimedDraftDocumentSignature

import pprint
PPP = pprint.PrettyPrinter(indent=4)

from toolkit.core.attachment.models import Revision


class Command(BaseCommand):
    args = '<revision pk ...>'
    help = "Test integration with HelloSign"

    slugs = []

    @property
    def records(self):
        return Revision.objects.filter(pk__in=self.slugs)

    def handle(self, *args, **options):
        self.slugs = args

        try:
            args[0]
        except IndexError:
            raise CommandError('You must specify a revision pk')

        for e in self.records:

            sd = e.primary_signdocument
            # #import pdb;pdb.set_trace()
            #resp = sd.send_for_signing(requester_email_address='ross@lawpal.com')
            resp = sd.create_unclaimed_draft(requester_email_address='ross@lawpal.com')
            print resp

            # s = HelloSignUnclaimedDraftDocumentSignature()
            # resp = s.detail(signature_request_id='ad1dfe0f9a666f5052ef201d667efd79bfa515ec', auth=("founders@lawpal.com", "test2007"))
            # import pdb;pdb.set_trace()
            # invitees = [
            #     {'name': 'Ross Customer', 'email': 'ross+customer@lawpal.com'},
            #     {'name': 'Ross Tech Lawyer', 'email': 'ross+lawyer@lawpal.com'}
            # ]

            # subject = 'Test Signing'
            # message = 'This is a test singing please delete'

            # doc_service = WordService()
            # document = doc_service.generate(html=e.html())

            # service = self.service(document=document, invitees=invitees, subject=subject, message=message)
            # result = service.send_for_signing(test_mode=1, client_id=settings.HELLOSIGN_CLIENT_ID)