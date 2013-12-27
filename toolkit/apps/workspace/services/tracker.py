# -*- coding: utf-8 -*-
"""
Integrate with https://github.com/adewinter/python-usps
forked to
https://github.com/rosscdh/python-usps

and the really ugly USPS xml api

xmlstr = ElementTree.tostring(et, encoding='utf8', method='xml')

"""
from django.conf import settings

import json

from usps.api import USPS_CONNECTION
from usps.api.tracking import TrackConfirmWithFields  # TrackConfirm

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

    @property
    def as_json(self):
        return json.dumps(self.response)

    @property
    def summary(self):
        return self.response.get('TrackSummary', {})

    @property
    def status(self):
        return self.summary.get('Event', 'Unknown')

    @property
    def description(self):
        s = self.summary.copy()
        country = s.get('EventCountry') if s.get('EventCountry') is not None else 'USA'
        return 'The package is currently %s in %s. The event took place on %s:%s' % (
                s.get('Event'),
                '%s %s %s, %s' % (s.get('EventCity'), s.get('EventState'), s.get('EventZIPCode'), country),
                s.get('EventDate'),
                s.get('EventTime'),)

    @property
    def waypoints(self):
        waypoints = self.response.get('TrackDetail', [])

        if self.summary:
            waypoints.insert(0, self.summary)  # insert the TrackSummary which is the "latest" waypoint Bad USPS Bad Bad Bad design

        return waypoints


class AdeWinterUspsTrackConfirm(object):
    """
    Send request out to USPS
    """
    USERID = getattr(settings, 'USPS_USERID')
    PASSWORD = getattr(settings, 'USPS_PASSWORD')
    USPS_CONNECTION = getattr(settings, 'USPS_CONNECTION', USPS_CONNECTION)

    tracking_code = None
    response = None

    @property
    def service(self):
        logger.info('Init USPS service with: %s %s' % (self.USPS_CONNECTION, self.USERID))

        return TrackConfirmWithFields(self.USPS_CONNECTION, self.USERID, self.PASSWORD)

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

        usps_log = instance.data.get('usps_log', [])
        usps_log.append(usps_response.response)

        usps['current_status'] = usps_response.description
        usps['status_code'] = usps_response.status
        usps['waypoints'] = usps_response.waypoints

        instance.data['usps'] = usps
        instance.data['usps_log'] = usps_log

        instance.save(update_fields=['data'])


class USPSTrackingService(AdeWinterUspsTrackConfirm):
    """
    Generic Accessor class imported by the system
    needs to extend the class we eventually decide to
    """
    pass
