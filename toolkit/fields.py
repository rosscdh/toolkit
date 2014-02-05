# -*- coding: utf-8 -*-
from django.forms import CharField

import bleach

from .widgets import SummernoteWidget


class SummernoteField(CharField):
    widget = SummernoteWidget

    attributes = {
        'blockquote': ['style',],
        'div': ['style',],
        'span': ['style',],
    }

    styles = [
        'border',
        'font-style',
        'font-weight',
        'margin',
        'padding',
        'text-align',
        'text-decoration',
    ]

    tags = [
        'blockquote',
        'br',
        'div',
        'li',
        'ol',
        'span',
        'ul',
    ]

    def __init__(self, tags=None, attributes=None, styles=None, strip=True, *args, **kwargs):
        super(SummernoteField, self).__init__(*args, **kwargs)

        self.strip = strip
        if tags is not None:
            self.tags = tags
        if attributes is not None:
            self.attributes = attributes
        if styles is not None:
            self.styles = styles

    def to_python(self, value):
        return bleach.clean(value, tags=self.tags, attributes=self.attributes, styles=self.styles, strip=self.strip)
