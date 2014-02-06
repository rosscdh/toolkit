from django.utils.unittest import TestCase

from ..fields import SummernoteField


class SummernoteFieldTests(TestCase):
    def test_to_python(self):
        # test that the field strips HTML by default
        f = SummernoteField(attributes=[], styles=[], tags=[])
        self.assertEqual(f.to_python('<p>Hello world!</p>'), 'Hello world!')

        # test that the field encodes HTML if strip=False
        f = SummernoteField(attributes=[], styles=[], tags=[], strip=False)
        self.assertEqual(f.to_python('<p>Hello world!</p>'), '&lt;p&gt;Hello world!&lt;/p&gt;')
