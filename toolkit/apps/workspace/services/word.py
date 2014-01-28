# -*- coding: utf-8 -*-
"""
HTML to Word Conversion Services
"""
from tempfile import NamedTemporaryFile

from .pandoc import BasePandocService

from . import logger


class PandocDocxService(BasePandocService):
    def generate(self, html, **kwargs):
        from_format = kwargs.get('from_format', 'html')
        to_format = kwargs.get('to_format', 'docx')
        # create temp file
        docx_file = NamedTemporaryFile(suffix='.docx')

        logger.info('Created .docx file at: %s' % (docx_file.name, ))

        # generate it using pandoc
        self.service.convert(html, to_format, format=from_format, extra_args=('--output', docx_file.name))
        # return the file which is now populated with the docx forms
        return docx_file


class WordService(PandocDocxService):
    """
    Generic Accessor class imported by the system
    needs to extend the class we eventually decide to
    """
    pass
