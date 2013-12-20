# -*- coding: utf-8 -*-
"""
Integrate with https://github.com/adewinter/python-usps
forked to
https://github.com/rosscdh/python-usps

and the really ugly USPS xml api
"""
from django.conf import settings

import json

from usps.api import USPS_CONNECTION_TEST
from usps.api.tracking import TrackConfirm

try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

from . import logger


class USPSTrackingNumberNotExistsException(Exception):
    message = 'USPS has no record of the specified tracking number.'


class USPSResponse(object):
    response = {}

    def __init__(self, usps_response, **kwargs):
        self.response = usps_response
        self.__dict__.update(**kwargs)  # passin variables

    def __str__(self):
        return self.status

    def __unicode__(self):
        return u'%s' % self.status

    def is_valid(self):
        return len(self.waypoints) > 0

    @property
    def as_json(self):
        return json.dumps(self.response)

    @property
    def status(self):
        return self.response.get('TrackSummary', 'No summary was supplied by USPS').strip()

    @property
    def waypoints(self):
        waypoints = self.response.get('TrackDetail', [])

        # assume: that there will always be at least 1 waypoint form when the package was registered
        # if not waypoints:
        #     raise USPSTrackingNumberNotExistsException(self.status)

        return waypoints


class AdeWinterUspsTrackConfirm(object):
    """
    Send request out to USPS
    """
    USERID = getattr(settings, 'USPS_USERID')
    PASSWORD = getattr(settings, 'USPS_PASSWORD')
    USPS_CONNECTION = getattr(settings, 'USPS_CONNECTION', USPS_CONNECTION_TEST)

    tracking_code = None
    response = None

    @property
    def service(self):
        logger.info('Init USPS service with: %s %s' % (self.USPS_CONNECTION, self.USERID))

        return TrackConfirm(self.USPS_CONNECTION, self.USERID, self.PASSWORD)

    def request(self, tracking_code):
        logger.info('Request USPS service: %s %s for tracking_code: %s' % (self.USPS_CONNECTION, self.USERID, tracking_code))
        response = []
        
        for r in self.service.execute([{'ID': tracking_code}]):
            usps_response = USPSResponse(usps_response=r, tracking_code=tracking_code)
            logger.info('USPS response for tracking_code: %s %s' % (usps_response.status, tracking_code))
            response.append(usps_response)

        return response[0] if len(response) == 1 else response

    def track(self, tracking_code):
        self.response = self.request(tracking_code=tracking_code)

        logger.info('Sent USPS tracking id request')

        return self.response

    def record(self, instance, usps_response):
        usps = instance.data.get('usps', {})

        usps['current_status'] = usps_response.status
        usps['waypoints'] = usps_response.waypoints

        instance.data['usps'] = usps
        instance.save(update_fields=['data'])


class USPSTrackingService(AdeWinterUspsTrackConfirm):
    """
    Generic Accessor class imported by the system
    needs to extend the class we eventually decide to
    """
    pass
