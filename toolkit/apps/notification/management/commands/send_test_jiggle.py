# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from toolkit.apps.notification.tasks import youve_got_notifications

import pprint


class Command(BaseCommand):
    """
    testing command to send the youve got notifications event for lees pusher integration
    """
    args = '<username>'
    help = "enter the username for which to send the test jiggle"

    def handle(self, *args, **options):
        username = None

        try:
            username = args
        except IndexError:
            #
            # Allow default to be used
            #
            PPP.pprint('Using default webhook_url sign:hellosign_webhook_event: %s' % self.callback_url)

        if username:
            youve_got_notifications(
                     username=username,
                     event='notifications.new',
                     detail='You have %d new notifications' % 10000000)
