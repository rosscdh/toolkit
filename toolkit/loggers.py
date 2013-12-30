# -*- coding: utf-8 -*-
from django.conf import settings
import logging

SPLUNKSTORM_ENDPOINT = getattr(settings, 'SPLUNKSTORM_ENDPOINT', None)
SPLUNKSTORM_PORT = getattr(settings, 'SPLUNKSTORM_PORT', None)

assert SPLUNKSTORM_ENDPOINT is not None, "You must define a SPLUNKSTORM_ENDPOINT in settings"
assert SPLUNKSTORM_PORT is not None, "You must define a SPLUNKSTORM_PORT in settings"


class SplunkStormLogger(logging.handlers.SysLogHandler):
    host = SPLUNKSTORM_ENDPOINT
    port = SPLUNKSTORM_PORT
    def __init__(self):
        super(SplunkStormLogger, self).__init__(address=(self.host, self.port,))
