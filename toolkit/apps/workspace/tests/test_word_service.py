# -*- coding: utf-8 -*-
import unittest
import inspect

from ..services import WordService
from ..services.word import PandocDocxService
from ..services.pandoc import BasePandocService


class DocxServiceTest(unittest.TestCase):
    subject = WordService

    def test_wordservice_is_valid(self):
        """
        Wordservice should inherit correctly
        """
        self.assertEqual(inspect.getmro(self.subject), (WordService,
                                                        PandocDocxService,
                                                        BasePandocService,
                                                        object))

    def test_valid_attribs(self):
        subject = self.subject()
        self.assertTrue(hasattr(subject, 'docx_file'))
        self.assertEqual(subject.docx_file, None)

    def test_valid_generation(self):
        subject = self.subject()
        html = '<html><body><h1>Yay</h1><p>the test <b>works</b></p></body></html>'

        resp = subject.generate(html=html)

        self.assertEqual(resp.__class__.__name__, '_TemporaryFileWrapper')

        subject_content = resp.read()
        resp.seek(0)  # reset pointer

        self.assertEqual(len(subject_content), 8394)
        # test we have the expected word gunk in there
        self.assertTrue('[Content_Types].xml' in subject_content)
        self.assertTrue('word/settings.xmlPK' in subject_content)
        self.assertTrue('word/fontTable.xmlPK' in subject_content)




