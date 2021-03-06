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

from toolkit.apps.eightythreeb.mailers import EightyThreeMailDeliveredEmail

from . import logger


class USPSTrackingNumberNotExistsException(Exception):
    message = 'USPS has no record of the specified tracking number.'


class USPSResponse(object):
    response = {}
    DELIVERED_STATUS = ['DELIVERED'] # must be uppercase to cater to the crappy usps api

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
    def identity(self):
        """
        The identity used to determine if this response is in the instance
        waypoints list
        """
        return '%s-%s-%s' % (self.summary.get('EventTime'),
                             self.summary.get('EventDate'),
                             self.summary.get('EventZIPCode'),)

    @property
    def waypoint_date(self):
        return '%s %s' % (self.summary.get('EventDate'), self.summary.get('EventTime'))
    @property
    def status(self):
        return self.summary.get('Event', 'Unknown')

    @property
    def is_delivered(self):
        return self.status.upper() in self.DELIVERED_STATUS

    def description(self, summary=None):
        s = self.summary if summary is None else summary

        country = s.get('EventCountry') if s.get('EventCountry') is not None else 'USA'
        location = None
        if s.get('EventCity') is not None and s.get('EventState') is not None and s.get('EventZIPCode'):
            location = 'in %s %s %s, %s' % (s.get('EventCity'), s.get('EventState'), s.get('EventZIPCode'), country,)

        return 'Current package status : %s %s. Last Updated :  %s:%s' % (
                s.get('Event'),
                location if location is not None else '',
                s.get('EventDate'),
                s.get('EventTime'),)

    @property
    def waypoints(self):
        waypoints = self.response.get('TrackDetail', [])
        if type(waypoints) is dict:
            # because were using XML, a single TrackDetail object will return as a dict
            # not as a list *sigh*
            waypoints = [waypoints]

        if self.summary and self.summary not in waypoints:
            # insert the TrackSummary which is the "latest" waypoint Bad USPS Bad Bad Bad design
            waypoints.insert(0, self.summary)

        return waypoints


class AdeWinterUspsTrackConfirm(object):
    """
    Send request out to USPS
    """
    USERID = getattr(settings, 'USPS_USERID')
    PASSWORD = getattr(settings, 'USPS_PASSWORD')
    USPS_CONNECTION = getattr(settings, 'USPS_CONNECTION', USPS_CONNECTION)

    blacklisted_events = (
        'Delivery status not updated',
    )

    tracking_code = None
    response = None

    _response_already_present = None

    @property
    def service(self):
        logger.info('Init USPS service with: %s %s' % (self.USPS_CONNECTION, self.USERID))

        return TrackConfirmWithFields(self.USPS_CONNECTION, self.USERID, self.PASSWORD)

    @property
    def response_already_present(self):
        return self._response_already_present

    def request(self, tracking_code):
        tracking_code = tracking_code.replace(' ', '')  # strip whitespace as the usps api does not support it

        logger.info('Request USPS service: %s %s for tracking_code: %s' % (self.USPS_CONNECTION, self.USERID, tracking_code))

        response = []
        
        for r in self.service.execute([{'ID': tracking_code}]):
            usps_response = USPSResponse(usps_response=r, tracking_code=tracking_code)

            logger.info('USPS response for tracking_code: %s %s' % (usps_response.status, tracking_code))
            response.append(usps_response)

        return response[0] if len(response) == 1 else response

    def response_is_present(self, instance_data, usps_response):
        waypoints = instance_data.get('waypoints', [])
        if waypoints:
            # Create the waypoint id and then compare it to the current 
            # responses identiy
            for point in waypoints:
                # Compare the id points and see if we have it already
                waypoint_id = '%s-%s-%s' % (point.get('EventTime'),
                                            point.get('EventDate'),
                                            point.get('EventZIPCode'),)

                if usps_response.identity == waypoint_id:
                    logger.info('The current response has already been recorded: %s %s' % (usps_response.identity, usps_response.status,) )
                    return True

        logger.info('The current response has not been recorded: %s %s' % (usps_response.identity, usps_response.status,) )

        return False

    def send_mail(self, instance, usps_response):
        recipient = (instance.user.get_full_name(), instance.user.email)

        lawyer = instance.workspace.lawyer
        from_tuple = (lawyer.get_full_name(), lawyer.email)

        mailer = EightyThreeMailDeliveredEmail(from_tuple=from_tuple,
                                               recipients=(recipient,))

        markers = instance.markers
        current_step = markers.current_marker
        next_step = current_step.next_marker

        mailer.process(instance=instance, usps_response=usps_response)

    def track(self, tracking_code):
        self.response = self.request(tracking_code=tracking_code)

        logger.info('Sent USPS tracking id request')

        return self.response

    def record(self, instance, usps_response):
        usps = instance.data.get('usps', {})

        if self.response_is_present(instance_data=usps, usps_response=usps_response) is True:
            self._response_already_present = True
            logger.info('Response was already present, not recording it')
        else:
            self._response_already_present = False
            logger.info('Response was not present, recording on instance: %s' % instance)

            usps_log = instance.data.get('usps_log', [])
            usps_log.append(usps_response.response)

            if usps_response.status in self.blacklisted_events:
                logger.info('Response was in the blacklist, setting current_status to be the previous waypoint but recording complete event: %s' % instance)
                # set the description to be 1 waypoint back as were in a blacklist event
                usps['current_status'] = usps_response.description(summary=usps_response.waypoints[1])
            else:
                usps['current_status'] = usps_response.description()

            usps['status_code'] = usps_response.status
            usps['waypoints'] = usps_response.waypoints

            instance.data['usps'] = usps
            instance.data['usps_log'] = usps_log

            instance.save(update_fields=['data'])

        # check for delivered event
        self.delivered(instance=instance, usps_response=usps_response)

    def delivered(self, instance, usps_response):
        if usps_response.is_delivered is True:
            self.send_mail(instance=instance, usps_response=usps_response)
            # Send the signal indicating we have completed this step
            instance.base_signal.send(sender=self, instance=instance, actor=instance.user, name='irs_recieved')


class USPSTrackingService(AdeWinterUspsTrackConfirm):
    """
    Generic Accessor class imported by the system
    needs to extend the class we eventually decide to
    """
    pass
