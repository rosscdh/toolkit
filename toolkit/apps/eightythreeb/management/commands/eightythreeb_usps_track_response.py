# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

from usps.errors import USPSXMLError

from toolkit.apps.workspace.services import USPSTrackingService

from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.mailers import EightyThreeMailDeliveredEmail


import logging
logger = logging.getLogger('django.request')


class Command(BaseCommand):
    help = "The cron for tracking USPS registered post"

    @property
    def service(self):
        if hasattr(self, '_service') is False or self._service is None:
            self._service = USPSTrackingService()
        return self._service

    @property
    def eightythreeb_list(self):
        return EightyThreeB.objects.mail_delivery_pending()

    def handle(self, *args, **options):
        site = Site.objects.get(pk=settings.SITE_ID)

        service = self.service

        for instance in self.eightythreeb_list:

            tracking_code = instance.tracking_code

            if tracking_code is None:
                logger.critical('Found 83b instance in track_response cycle with no tracking_code: %s %s' % (instance, tracking_code))
            else:
                logger.info('Found 83b instance with tracking_code: %s %s' % (instance, tracking_code))

                try:
                    usps_response = service.track(tracking_code=tracking_code)
                    service.record(instance=instance, usps_response=usps_response)

                except USPSXMLError as e:
                    logger.error('83b instance raised Exception: %s %s %s' % (instance, tracking_code, e))
