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

from dateutil import parser
import math

class MissingMarkersException(Exception):
    msg = 'You must have at least 1 marker item in the object.signal_map list attribute'


class BaseSignalMarkers(object):
    tool_object = None
    signal_map = []
    markers_map = {
        'previous': None,
        'current': None,
        'next': None,
    }

    def __init__(self, tool=None):
        if tool is not None:
            self.tool = tool
        self.previous = None

        try:
            self.current = self.signal_map[0]

        except IndexError:
            raise MissingMarkersException

        try:
            self.next = self.signal_map[1]

        except IndexError:
            self.next = None

        self._set_markers_fsm()  # finite state machine

    def _set_markers_fsm(self):
        for i, marker in enumerate(self.signal_map):
            # set the marker prev and next
            signal = self.signal_map[i]

            try:
                marker.previous = self.signal_map[i-1]
            except IndexError:
                marker.previous = None

            try:
                marker.next = self.signal_map[i+1]
            except IndexError:
                marker.next = None

            # if the next marker is incomplete and the previous is complete then we have our current
            if marker.next is not None and marker.next.is_complete is False:
                if marker.previous is not None and marker.previous.is_complete is True:
                    self.current = signal
                    self.previous = marker.previous
                    self.next = marker.next


    def __iter__(self):
        return iter(self.signal_map)

    @property
    def tool(self):
        return self.tool_object

    @tool.setter
    def tool(self, tool):
        self.tool_object = tool
        for s in self.signal_map:
            s.tool = self.tool_object

    @property
    def num_markers(self):
        return len(self.signal_map)

    @property
    def percent_complete(self):
        markers = self.tool.data['markers']
        whole = self.num_markers

        part = 0
        for i in self.signal_map:
            part = (part + 1) if i.name in markers else part
        percent = 100 * float(part)/float(whole)
        return float("{0:.2f}".format(math.ceil(percent)))

    def marker(self, val):
        if type(val) in [str, unicode]:
            return self.marker_by_name(name=val)
        if type(val) in [int, float]:
            return self.marker_by_val(val=val)
        return None

    def marker_by_val(self, val):
        for i, marker in enumerate(self.signal_map):
            if val == marker.val:
                return marker
        return None

    def marker_by_name(self, name):
        for i, marker in enumerate(self.signal_map):
            if name == marker.name:
                return marker
        return None

    @property
    def current(self):
        return self.markers_map.get('current')

    @current.setter
    def current(self, value):
        self.markers_map['current'] = value

    @property
    def next(self):
        return self.markers_map.get('next')

    @next.setter
    def next(self, value):
        self.markers_map['next'] = value

    @property
    def previous(self):
        return self.markers_map.get('previous')

    @previous.setter
    def previous(self, value):
        self.markers_map['previous'] = value

    def named_tuple(self, name):
        """
        Return named tuple for model status use
        """
        named_tuple = [(signal_marker.val, signal_marker.name, signal_marker.description) for signal_marker in self.signal_map]
        return get_namedtuple_choices(name, tuple(named_tuple))


class Marker(object):
    ACTION_TYPE = get_namedtuple_choices('ACTION_TYPE', (
                    (0, 'remote', 'Remote'),
                    (1, 'redirect', 'Redirect'),
                    (2, 'modal', 'Modal'),
                ))

    tool = None
    val = None

    name = None
    description = None
    _long_description = None
    signals = []

    action_name = None

    action_type = None
    action = None

    action_user_class = []  # must be a list so we can handle multiple types

    markers_map = {
        'previous': None,
        'next': None,
    }

    next = None
    previous = None

    def __init__(self, val, **kwargs):
        self.val = val

        name = kwargs.pop('name', None)
        if name is not None:
            self.name = name

        description = kwargs.pop('description', None)
        if description is not None:
            self.description = description

        long_description = kwargs.pop('long_description', None)  # set the long description to the description as it will get overriden if the user actually sets long_description
        if long_description is not None:
            self._long_description = long_description

        signals = kwargs.pop('signals', None)
        if signals is not None:
            self.signals = signals

        # use the locally defined def action if exists otherwise if an
        # action is passed in; use that
        if hasattr(self, 'action_name') is False and 'action_name' in kwargs:
            self.action_name = kwargs.pop('action_name')

        if hasattr(self, 'action') is False and 'action' in kwargs:
            self.action = kwargs.pop('action')

        if hasattr(self, 'action_user_class') is False and 'action_user_class' in kwargs:
            self.action_user_class = kwargs.pop('action_user_class')

        next = kwargs.pop('next', None)
        if next is not None:
            self.next = next

        previous = kwargs.pop('previous', None)
        if previous is not None:
            self.previous = previous

        tool = kwargs.pop('tool', None)
        if tool is not None:
            self.tool = tool

        self.data = kwargs

    def __str__(self):
        return u'{name}'.format(name=self.name).encode('utf-8')

    @property
    def desc(self):
        self.description

    @property
    def next(self):
        return self.markers_map.get('next')

    @next.setter
    def next(self, value):
        self.markers_map['next'] = value

    @property
    def previous(self):
        return self.markers_map.get('previous')

    @previous.setter
    def previous(self, value):
        self.markers_map['previous'] = value

    @property
    def status(self):
        if self.is_complete:
            return 'done'

        if  self.previous.is_complete and not self.next.is_complete:
            return 'next'

        return 'pending'

    @property
    def is_complete(self):
        if self.tool is not None:
            return self.name in self.tool.data['markers']
        return False

    @property
    def date_completed(self):
        if self.is_complete:
            return parser.parse(self.tool.data['markers'][self.name].get('date_of'))
        return None

    @property
    def action_attribs(self):
        attribs = {}
        # Handle the modal action_type
        if self.action_type == self.ACTION_TYPE.modal:
            attribs.update({
                'target': '#%s' % getattr(self, 'modal_target', 'modal-%s' % self.name)  ## if we have the attribute modal_target use it else use self.name
            })

        return attribs

    def get_action_url(self):
        """
        method used to return the marker action_url without display business logic
        """
        raise NotImplementedError

    @property
    def long_description(self):
        return self._long_description if self.is_complete is False else None

    @long_description.setter
    def long_description(self, value):
        self._long_description = value

    @property
    def action(self):
        return self.get_action_url()

    def tool_info(self):
        if self.tool is not None:
            if hasattr(self.tool, 'data') and 'markers' in self.tool.data and self.name in self.tool.data['markers']:
                return self.tool.data['markers'][self.name]
        return False

    def issue_signals(self, request, instance, actor):
        for s in self.signals:
            method = _class_importer(s)  # @TODO can optimise this and precache them
            method.send(sender=request, instance=instance, actor=actor)
