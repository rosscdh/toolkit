# -*- coding: utf-8 -*-
"""
HTML to Word Conversion Services
"""
import pypandoc


class BasePandocService(object):
    """
    Base class for converting provided HTML to a doc or docx
    """
    options = None

    def __init__(self):
        self.service = self.get_service()

    def get_service(self):
        return pypandoc

    def generate(self, **kwargs):
        raise NotImplementedError