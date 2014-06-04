# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from toolkit.core.services.reminder import ReminderService


class Command(BaseCommand):
    help = 'Collects items in need of a reminder'

    def handle(self, *args, **options):
        service = ReminderService()
        service.process()