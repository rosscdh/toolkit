# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from hello_sign.models import HelloSignRequest

from toolkit.apps.sign.tasks import _download_signing_complete_document

from termcolor import colored


class Command(BaseCommand):
    """
    Command to download and complete a documetn sent for signing
    Used when the final HelloSign webhook fails to present itself:
    """
    args = '<HelloSignRequest_pk_or_signature_request_id>'
    help = "Pass in a HelloSignRequest object pk or signature_request_id to download and complete the signing manually i.e. ./manage.py execute_document_manually 2a4950ac78f80677fa105d4aede646fdb1d47e57 98 ..."

    def handle(self, *args, **options):
        self.pks = self.get_hs_request_object_pks(*args)

        if not self.pks:
            raise CommandError('No HelloSignRequest objects found with %s as identifiers' % args)
        else:
            for hs_request in HelloSignRequest.objects.filter(pk__in=self.pks):
                print(colored('Downloading hs_request %s (%d) ' % (hs_request.signature_request_id, hs_request.pk), 'red'))
                #
                # Perform the download synchronously as we want to see what happens
                #
                _download_signing_complete_document(hellosign_request=hs_request)


    def get_hs_request_object_pks(self, *args):
        pk_set = []
        if len(args) <= 0:
            raise CommandError('Please specify a HelloSignRequest.pk or HelloSignRequest.signature_request_id')

        for _id in args:

            try:
                _id = int(_id)
            except ValueError:
                try:
                    obj = HelloSignRequest.objects.get(signature_request_id=_id)
                    _id = obj.pk
                except HelloSignRequest.DoesNotExist:
                    _id = None

            if _id:
                pk_set.append(_id)

        return pk_set