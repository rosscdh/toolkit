# -*- coding: utf-8 -*-
from django.forms import CharField

from .widgets import SummerNoteWidget


class SummerNoteField(CharField):
    widget = SummerNoteWidget