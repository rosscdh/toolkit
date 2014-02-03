# -*- coding: utf-8 -*-
from django.dispatch import Signal


""" HelloSign webhook Event """
hellosign_webhook_event_recieved = Signal(providing_args=['signature_request_id', 'event_type', 'data', 'hellosign_request', 'hellosign_log'])