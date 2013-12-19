# -*- coding: utf-8 -*-
"""
Services to the workspace
"""
import logging
logger = logging.getLogger('django.request')


from .customer import EnsureCustomerService
from .pdf import PDFKitService
from .tracker import USPSTrackingService
