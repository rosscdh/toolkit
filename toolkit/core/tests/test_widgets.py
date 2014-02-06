from django.test import TestCase

from ..widgets import SummernoteWidget


class SummernoteWidgetTests(TestCase):
    def test(self):
        w = SummernoteWidget()
        self.assertHTMLEqual(w.render('foo', ''), '<textarea cols="100" data-toggle="summernote" name="foo" />')
        self.assertHTMLEqual(w.render('foo', 'bar'), '<textarea cols="100" data-toggle="summernote" name="foo">bar</textarea>')

        # You can also pass 'attrs' to the constructor:
        w = SummernoteWidget(attrs={'cols': '20'})
        self.assertHTMLEqual(w.render('foo', ''), '<textarea cols="20" data-toggle="summernote" name="foo" />')
        self.assertHTMLEqual(w.render('foo', 'bar'), '<textarea cols="20" data-toggle="summernote" name="foo">bar</textarea>')
