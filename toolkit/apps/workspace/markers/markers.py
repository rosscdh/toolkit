# -*- coding: utf-8 -*-
from toolkit.utils import get_namedtuple_choices
from toolkit.utils import _class_importer

from dateutil import parser


BASE_MARKER_ACTION_TYPES = get_namedtuple_choices('ACTION_TYPE', (
                                (0, 'remote', 'Remote'),
                                (1, 'redirect', 'Redirect'),
                                (2, 'modal', 'Modal'),
                            ))


class Marker(object):
    ACTION_TYPE = BASE_MARKER_ACTION_TYPES

    # overridden with customer .getter and .setter
    _tool = None
    _description = None
    _long_description = None

    val = None
    name = None
    signals = []

    action_name = None
    action_type = None
    action = None
    action_user_class = []  # must be a list so we can handle multiple types

    is_prerequisite = False  # Prerequisite class used to override this
    hide_when_complete = False  # Prerequisite is set to True

    markers_map = {
        'previous': None,
        'next': None,
    }

    def __init__(self, val, *args, **kwargs):
        self.val = val

        self.name = kwargs.pop('name', self.name)
        self._description = kwargs.pop('description', self._description)
        self._long_description = kwargs.pop('long_description', self._long_description)  # set the long description to the description as it will get overriden if the user actually sets long_description
        self.signals = kwargs.pop('signals', self.signals)
 
        # use the locally defined def action if exists otherwise if an
        # action is passed in; use that
        if hasattr(self, 'action_name') is False and 'action_name' in kwargs:
            self.action_name = kwargs.pop('action_name')

        if hasattr(self, 'action') is False and 'action' in kwargs:
            self.action = kwargs.pop('action')

        if hasattr(self, 'action_user_class') is False and 'action_user_class' in kwargs:
            self.action_user_class = kwargs.pop('action_user_class')

    def __repr__(self):
        return u'<Marker: {val}:{name}>'.format(name=self.name, val=self.val).encode('utf-8')

    def __str__(self):
        return u'{name}'.format(name=self.name).encode('utf-8')

    @property
    def tool(self):
        return self._tool

    @tool.setter
    def tool(self, value):
        self._tool = value

    @property
    def next_marker(self):
        next_marker = self.markers_map.get('next')
        #
        # keep looping until we find a marker that can be shown
        # @BUSINESSRULE Prerequisite markers
        #
        while next_marker is not None and next_marker.show_marker is False:
            next_marker = next_marker.next_marker
        return next_marker

    @next_marker.setter
    def next_marker(self, value):
        #print "set Marker(%s).next_marker: %s" % (self, value)
        self.markers_map['next'] = value

    @property
    def previous_marker(self):
        previous_marker = self.markers_map.get('previous')
        #
        # keep looping until we find a marker that can be shown
        # @BUSINESSRULE Prerequisite markers
        #
        while previous_marker is not None and previous_marker.show_marker is False:
            previous_marker = previous_marker.previous_marker
        return previous_marker

    @previous_marker.setter
    def previous_marker(self, value):
        #print "set Marker(%s).previous_marker: %s" % (self, value)
        self.markers_map['previous'] = value

    @property
    def status(self):
        if self.is_complete:
            return 'done'

        elif self.is_current:
            return 'next'

        return 'pending'

    @property
    def is_current(self):
        return self.tool.markers.current_marker == self

    @property
    def is_complete(self):
        if self.tool is not None:
            markers = self.tool.data.get('markers', {})
            return self.name in markers.keys()
        return False

    @property
    def date_completed(self):
        if self.is_complete:
            return parser.parse(self.tool.data['markers'][self.name].get('date_of'))
        return None

    @property
    def action_type_name(self):
        return self.ACTION_TYPE.get_name_by_value(self.action_type) if self.action_type is not None else None

    @property
    def action_attribs(self):
        attribs = {}
        # Handle the modal action_type
        if self.action_type == self.ACTION_TYPE.modal:
            attribs.update({
                'target': '#%s' % getattr(self, 'modal_target', 'modal-%s' % self.name),  ## if we have the attribute modal_target use it else use self.name
                'toggle': "modal",
            })
        elif self.action_type == self.ACTION_TYPE.remote or self.action_type == self.ACTION_TYPE.redirect:
            attribs.update({'toggle': 'action'})

        return attribs

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def long_description(self):
        return self._long_description if self.is_complete is False else None

    @long_description.setter
    def long_description(self, value):
        self._long_description = value

    @property
    def action(self):
        return self.get_action_url()

    @property
    def show_marker(self):
        if self.tool is not None:
            if hasattr(self, 'hide_when_complete') is True:
                return (self.hide_when_complete is True and self.is_complete is True) is False
        return True


    def can_perform_action(self, user):
        """
         @BUSINESS_RULE
         show the action to user that have the right class OR where the user
         does not have the right class but IS the object.user but the action class
         is not lawyers only
        """
        if self.action is not None and \
            (user.profile.user_class in self.action_user_class or \
            user.profile.user_class not in self.action_user_class and user == self.tool.user and self.action_user_class != ['lawyer']):
            return True

        return False

    def get_action_url(self):
        """
        method used to return the marker action_url without display business logic
        """
        raise NotImplementedError

    def tool_info(self):
        if self.tool is not None:
            if hasattr(self.tool, 'data') and 'markers' in self.tool.data and self.name in self.tool.data['markers']:
                return self.tool.data['markers'][self.name]
        return False

    def issue_signals(self, request, instance, actor, **kwargs):
        for s in self.signals:
            method = _class_importer(s)  # @TODO can optimise this and precache them
            method.send(sender=request, instance=instance, actor=actor, **kwargs)

    def on_complete(self):
        """
        Method to allow markers to perform specific actions when they are completed
        """
        raise NotImplementedError
