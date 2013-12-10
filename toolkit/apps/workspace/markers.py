# -*- coding: utf-8 -*-
"""
Simple LinkedList implementation
For tracking Nodes and Edges that will allow us to have
next() and prev() and allow traversal through the document flows

>>> from toolkit.apps.eightythreeb import EIGHTYTHREEB_STATUS
>>> from toolkit.apps.eightythreeb.markers import Marker
>>> nodes = []
>>> for val, name, desc in EIGHTYTHREEB_STATUS.get_all():
>>>     nodes.append(Marker(val, name, desc, signals=[], next=None, previous=None))

"""
from toolkit.utils import get_namedtuple_choices
from toolkit.utils import _class_importer


class BaseSignalMarkers(object):
    tool_object = None
    signal_map = []

    @property
    def tool(self):
        return self.tool_object

    @tool.setter
    def tool(self, tool):
        self.tool_object = tool
        for s in self.signal_map:
            s.tool = self.tool_object

    def marker(self, val):
        for s in self.signal_map:
            if val == s.val:
                return s
        return None

    def named_tuple(self, name):
        """
        Return named tuple for model status use
        """
        named_tuple = [(signal_marker.val, signal_marker.name, signal_marker.description) for signal_marker in self.signal_map]
        return get_namedtuple_choices(name, tuple(named_tuple))


class Marker:
    tool = None
    name = None
    description = None
    long_description = None
    val = None
    signals = None
    next = None
    previous = None

    def __init__(self, val, name, description, **kwargs):
        self.val = val
        self.name = name
        self.description = description

        self.long_description = kwargs.pop('long_description', None)

        self.signals = kwargs.pop('signals', [])
        self.next = kwargs.pop('next', None)
        self.previous = kwargs.pop('previous', None)

        self.tool = kwargs.pop('tool', None)

        self.data = kwargs

    def __str__(self):
        return str(self.data)

    @property
    def is_complete(self):
        if self.tool is not None:
            return self.name in self.tool.data['markers']
        return False

    def tool_info(self):
        if self.tool is not None:
            if hasattr(self.tool, 'data') and 'markers' in self.tool.data and self.name in self.tool.data['markers']:
                return self.tool.data['markers'][self.name]
        return False

    def issue_signals(self, request, instance, actor):
        for s in self.signals:
            method = _class_importer(s)
            method.send(sender=request, instance=instance, actor=actor)
