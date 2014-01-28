# -*- coding: utf-8 -*-
from django.forms.widgets import Textarea


class SummerNoteWidget(Textarea):
    custom_attrs = {
        'data-toggle': 'summernote',
        'cols': '100',
    }

    class Media:
        css = {
            'all': ('css/summernote.css',),
        }
        js = ('js/summernote.min.js',)

    def __init__(self, *args, **kwargs):
        self.custom_attrs.update(kwargs.get('attrs', {}))
        attrs = self.custom_attrs.copy()
        super(SummerNoteWidget, self).__init__(attrs=attrs, *args, **kwargs)