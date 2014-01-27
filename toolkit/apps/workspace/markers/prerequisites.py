# -*- coding: utf-8 -*-
from .markers import Marker


class Prerequisite(Marker):
    """
    A prerequisite that will evaluate wether a given condition is true
    if not true then the action_url is returned
    p = Prerequisite(1)
    p.action = None  # this means the prerequisite has been met and we can hide the marker
    p.action = /url/to/place/  # this means the prerequisite has not been met
    """
    val = 0
    is_prerequisite = True
    hide_when_complete = True
    workspace = None  # required so we can evaluate without tool which we dont have on tool.create
