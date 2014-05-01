# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

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

            sd = e.signdocument_set.all().first()
            resp = sd.send_for_signing()
            print resp.json()

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