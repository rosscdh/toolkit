# -*- coding: utf-8 -*-
import os

try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

TRACK_RESPONSE_XML = ET.parse('%s/usps_trackfield_response.xml' % FILE_PATH)
TRACK_RESPONSE_XML_BODY = ET.tostring(TRACK_RESPONSE_XML.getroot(), encoding='utf8', method='xml')