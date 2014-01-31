# -*- coding: utf-8 -*-
from django.forms import CharField

from .widgets import SummernoteWidget


class SummernoteField(CharField):
    widget = SummernoteWidget
