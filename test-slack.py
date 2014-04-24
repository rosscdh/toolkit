# -*- coding: utf-8 -*-
from slack.endpoints import SlackChannelMessage


service = SlackChannelMessage(channel='general')
service.process(message='testing 123', username='rosscdh')