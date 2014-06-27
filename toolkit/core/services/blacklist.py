# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from toolkit.core.services.analytics import AtticusFinch

import logging
logger = logging.getLogger('django.request')


class BlackListService(object):
    """
    Maintain a set of blacklisted ip addresses
    """
    def __init__(self, request, **kwargs):
        self.analytics = AtticusFinch()

        self.request = request
        self.user = request.user
        self.ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

    @property
    def ip_blacklist(self):
        return cache.get('ip_blacklist', [])

    @ip_blacklist.setter
    def ip_blacklist(self, ip_address):
        ip_blacklist = self.ip_blacklist
        ip_blacklist.append(ip_address)
        # set the value
        cache.set('ip_blacklist', ip_blacklist, timeout=None) # cache forever
        logger.info('Banned IP_ADDRESS List: %s' % ip_blacklist)

    def is_blacklisted(self, ip_address=None):
        ip_address = self.ip_address if ip_address is None else ip_address
        return ip_address in self.ip_blacklist

    def blacklist_ip(self, ip_address=None):
        ip_address = self.ip_address if ip_address is None else ip_address
        if ip_address not in self.ip_blacklist:
            # add to the blacklist
            self.ip_blacklist = ip_address
            # log
            logger.critical('Banned IP_ADDRESS: %s' % ip_address)
            # record that event
            self.analytics.event('user.login', ip_address=ip_address)

    def process(self, *kwargs):
        if self.is_blacklisted(ip_address=kwargs.get('ip_address')) is True:
            self.blacklist_ip(ip_address=kwargs.get('ip_address'))
            self.forbid()

    def forbid(self):
        raise PermissionDenied()