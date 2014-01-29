# -*- coding: utf-8 -*-
"""
HTML to Word Conversion Services
"""
from django.core.files import File
from tempfile import NamedTemporaryFile

from .pandoc import BasePandocService

from . import logger


class PandocPDFService(BasePandocService):
    docx_file = None

    def generate(self, html, **kwargs):
        from_format = kwargs.get('from_format', 'html')
        to_format = kwargs.get('to_format', 'tex')
        # create temp file
        self.docx_file = NamedTemporaryFile(suffix='.pdf')

        logger.info('Created .docx file at: %s' % (self.docx_file.name, ))

        extra_args = (
            '--smart',
            '--standalone',
            '-o', self.docx_file.name
        )
        # generate it using pandoc
        self.service.convert(html, to_format, format=from_format, extra_args=extra_args)
        # return the file which is now populated with the docx forms
        return self.docx_file


class PandocDocxService(BasePandocService):
    docx_file = None

    def generate(self, html, **kwargs):
        from_format = kwargs.get('from_format', 'html')
        to_format = kwargs.get('to_format', 'docx')
        # create temp file
        self.docx_file = NamedTemporaryFile(suffix='.docx')

        logger.info('Created .docx file at: %s' % (self.docx_file.name, ))

        extra_args = (
            '--smart',
            '--standalone',
            '-o', self.docx_file.name
        )
        # generate it using pandoc
        self.service.convert(html, to_format, format=from_format, extra_args=extra_args)
        # return the file which is now populated with the docx forms
        return File(self.docx_file)

class WordService(PandocDocxService):
    """
    Generic Accessor class imported by the system
    needs to extend the class we eventually decide to
    """
    pass
