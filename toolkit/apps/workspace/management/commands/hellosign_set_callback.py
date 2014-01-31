# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import pprint
import requests

PPP = pprint.PrettyPrinter(indent=4)


class Command(BaseCommand):
    """
    Manually:
    using https://github.com/jkbr/httpie
    http -a <emakl>:<password> -f POST https://api.hellosign.com/v3/account callback_url=https://2b2dea03.ngrok.com/sign/hellosign/event/
    """
    args = '<callback_url>'
    help = "Register or update the callback_url for your environment at hellosign"
    endpoint = 'https://api.hellosign.com/v3/account'
    service = requests

    def handle(self, *args, **options):
        self.callback_url = args[0]

        try:
            self.callback_url = args[0]
        except IndexError:
            raise CommandError('You must specify a callback_url')

        resp = self.service.post(self.endpoint, auth=settings.HELLOSIGN_AUTHENTICATION, data={'callback_url': self.callback_url})

        print('Status Code: %s' % resp.status_code)
        PPP.pprint(resp.json())
