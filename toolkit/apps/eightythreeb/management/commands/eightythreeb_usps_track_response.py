# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

from toolkit.apps.workspace.services import USPSTrackingService

from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.mailers import EightyThreeMailDeliveredEmail


import logging
logger = logging.getLogger('django.request')


class Command(BaseCommand):
    help = "The cron for tracking USPS registered post"
    from_tuple = ('Ross', 'ross@lawpal.com')

    @property
    def service(self):
      if hasattr(self, '_service') is False or self._service is None:
        self._service = USPSTrackingService()
      return self._service

    @property
    def eightythreeb_list(self):
        return EightyThreeB.objects.mail_delivery_pending()

    def send_mail(self, instance):
        recipient = (instance.user.get_full_name(), instance.user.email)
        mailer = EightyThreeMailDeliveredEmail(from_tuple=self.from_tuple,  \
                                               recipients=(recipient,))

        markers = instance.markers
        current_step = markers.current
        next_step = current_step.next

        mailer.process(instance=instance)

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

                    if usps_response.is_delivered is True and service.response_already_present is False:
                        self.send_mail(instance=instance)
                        # Send the signal indicating we have completed this step
                        instance.base_signal.send(sender=self, instance=instance, actor=instance.user, name='irs_recieved')

                except Exception as e:
                  logger.error('83b instance raised Exception: %s %s %s' % (instance, tracking_code, e))
