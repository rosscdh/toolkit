# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.mailers import EightyThreeBReminderEmail


class Command(BaseCommand):
    help = "The reminder cron for 83b applications"

    @property
    def eightythreeb_list(self):
        return EightyThreeB.objects.incomplete()

    def handle(self, *args, **options):
        site = Site.objects.get(pk=settings.SITE_ID)

        for instance in self.eightythreeb_list:
            recipient = (instance.user.get_full_name(), instance.user.email)

            mailer = EightyThreeBReminderEmail(recipients=(recipient,))

            markers = instance.markers
            current_step = markers.current
            next_step = current_step.next

            mailer.process(company=instance.workspace, \
                           url='%s%s' % (site.domain[0:-1], instance.get_absolute_url()), \
                           current_status=current_step.long_description, \
                           next_step=next_step.long_description if next_step is not None else None, \
                           current_step=current_step.val, \
                           total_steps=markers.num_markers, \
                           num_days_left=instance.days_left,
                           percent_complete=markers.percent_complete,
                           instance=instance)