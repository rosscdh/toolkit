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

from .mixins import (MARKERS_MAP_DICT,
                     MarkerMapMixin)

import math
import copy


class MissingMarkersException(Exception):
    msg = 'You must have at least 1 marker item in the object.signal_map list attribute'


class BaseSignalMarkers(MarkerMapMixin, object):
    """
    Workflow Class that holds a set of Markers that are used to establish the
    flow
    """
    markers_map = {}
    signal_map = []
    prerequisite_signal_map = []

    _tool = None

    def __init__(self, tool=None, *args, **kwargs):
        super(BaseSignalMarkers, self).__init__(*args, **kwargs)
        #
        # Re initialise the local markers_map
        #
        self.markers_map = copy.copy(MARKERS_MAP_DICT)
        #
        # Ensure we have at least 1 item in the signal_map
        #
        try:
            self.signal_map[0]
        except IndexError:
            raise MissingMarkersException

        self._set_markers_navigation()  # finite state machine
        self.set_navigation_based_on_tool()  # reset the markers_map based

        if tool is not None:  # only if its passed in
            self.tool = tool

    def _set_markers_navigation(self):
        """
        Set the next previous and current values for the base class 
        as well as the specific markers
        """

        for i, marker in enumerate(self.signal_map):
            self.current_marker = marker
            """
            **python suprise**
            python lists list[-1] will return the last item on the list
            and not the expected i-1 == 0 if i == 0, i-1 will return -1
            which..returns the last on the list and not the first
            """
            self.previous_marker = None
            if i > 0:
                self.previous_marker = self.signal_map[i-1]

            try:
                self.next_marker = self.signal_map[i+1]
            except IndexError:
                self.next_marker = None

            #
            # Copy the current version of the base marker map
            #
            copy_marker_map = copy.copy(self.markers_map)
            del copy_marker_map['current'] # the markers dotn have a current as the "are" the current
            self.signal_map[i].markers_map = copy_marker_map

    def __iter__(self):
        return iter(self.signal_map)

    @property
    def percent_complete(self):
        markers = self.tool.data.get('markers', {})
        whole = self.num_markers

        part = 0
        for i in self.signal_map:
            part = (part + 1) if i.name in markers else part

        percent = 100 * float(part)/float(whole)

        return float("{0:.2f}".format(math.ceil(percent)))

    @property
    def tool(self):
        return self._tool

    @tool.setter
    def tool(self, tool):
        self._tool = tool

        # set the tool for each Marker
        for i, marker in enumerate(self.signal_map):
            marker.tool = self._tool

        # set the current next etc
        self.set_navigation_based_on_tool()

    def prerequisite_next_url(self, workspace):
        for klass in self.prerequisite_signal_map:

            prereq = klass(val=0, workspace=workspace)
            prereq.workspace = workspace
            #
            # if we have an incomplete marker
            # then return its url instead
            #
            if prereq.is_complete is False:
                return prereq.get_action_url()

        return None

    def set_navigation_based_on_tool(self):
        # Set Navigation based on tool status
        # get teh marker based on the tools status
        # if no tool then set marker to be the first in line
        marker = self.marker(self._tool.status) if self._tool is not None else self.signal_map[0]

        self.current_marker = marker
        self.next_marker = marker.next_marker
        self.previous_marker = marker.previous_marker
        #print "Update Marker Nav: current:%s next:%s previous:%s" % (marker, self.next_marker, self.previous_marker)

    def named_tuple(self, name):
        """
        Return named tuple for model status use
        """
        named_tuple = [(signal_marker.val, signal_marker.name, signal_marker.description) for signal_marker in self.signal_map]
        return get_namedtuple_choices(name, tuple(named_tuple))
