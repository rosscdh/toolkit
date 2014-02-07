from django.utils.unittest import TestCase

from ..fields import HTMLField


class HTMLFieldTests(TestCase):
    def test_microsoft_word_html(self):
        # test that we strip Microsoft Word HTML
        f = HTMLField()
        self.assertEqual(f.to_python("<p class=MsoNormal style='margin-top:3.0pt;margin-right:0in;margin-bottom:0in;margin-left:.2in;margin-bottom:.0001pt;text-indent:-.2in'>Hello world!</p>"), 'Hello world!')
        self.assertEqual(f.to_python("<p style='margin-top:3.0pt;margin-right:0in;margin-bottom:0in;margin-left:.2in;margin-bottom:.0001pt;text-indent:-.2in'><a name=ahali></a><b>Hello</b> <i>[...]</i> world!</p>"), 'Hello [...] world!')
