# -*- coding: utf-8 -*-

MARKERS_MAP_DICT = {
    'previous': None,
    'current': None,
    'next': None,
}


class PrerequisitesMixin(object):
    """
    Class to contain functionality relating to Prerequisistes
    which are Markers that must be is_complete=True before the user can continue
    with the process flow
    """
    prerequisite_signal_map = []  # list of prereqs to instantiate
    _prerequisites = {}  # cache the prereq by class.name

    def __init__(self, tool=None, *args, **kwargs):
        self._prerequisites = kwargs.get('_prerequisites', {})
        super(PrerequisitesMixin, self).__init__(*args, **kwargs)

    def prerequisites(self, workspace, **kwargs):
        # simple caching of prereq classes
        for klass in self.prerequisite_signal_map:
            self._prerequisites[klass.name] = self._prerequisites.get(klass.name, klass(val=0, workspace=workspace))

        return self._prerequisites.values()  # return the actual class instances and not the keys

    def prerequisite_next_url(self, workspace):
        for prereq in self.prerequisites(workspace=workspace):
            prereq.workspace = workspace
            #
            # if we have an incomplete marker
            # then return its url instead
            #
            if prereq.is_complete is False:
                return prereq.get_action_url()

        return None


class MarkerMapMixin(object):
    """
    Mixin to allow access to Markers via the signal_map
    attribute
    """
    markers_map = MARKERS_MAP_DICT

    @property
    def num_markers(self):
        return len(self.signal_map)

    @property
    def current_marker(self):
        return self.markers_map.get('current')

    @current_marker.setter
    def current_marker(self, value):
        self.markers_map['current'] = value

    @property
    def next_marker(self):
        return self.markers_map.get('next')

    @next_marker.setter
    def next_marker(self, value):
        self.markers_map['next'] = value

    @property
    def previous_marker(self):
        return self.markers_map.get('previous')

    @previous_marker.setter
    def previous_marker(self, value):
        self.markers_map['previous'] = value

    def marker(self, val):
        val_type = type(val)
        if val_type in [str, unicode]:
            return self.marker_by_name(name=val)

        elif val_type in [int, float]:
            return self.marker_by_val(val=val)

        raise Exception('No Marker of type: %s' % val)

    def marker_by_val(self, val):
        for marker in self.signal_map:
            if val == marker.val:
                return marker
        raise Exception('No Marker of val: %s' % val)

    def marker_by_name(self, name):
        for marker in self.signal_map:
            if name == marker.name:
                return marker
        raise Exception('No Marker of name: %s' % name)