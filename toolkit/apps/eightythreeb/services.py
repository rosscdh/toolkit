# -*- coding: utf-8 -*-

from .models import EightyThreeB


class TrackingCodeService(object):
    """
    Service to process the tracking code USPS response
    """
    def __init__(self):
        self.pending_83bs = EightyThreeB.objects.mail_delivery_pending()

    def process(self, tracking_code):
        for item in self.pending_83bs:
            pass
