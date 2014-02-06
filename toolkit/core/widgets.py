from django.forms.widgets import Textarea


class SummernoteWidget(Textarea):
    custom_attrs = {
        'data-toggle': 'summernote',
        'cols': '100',
    }

    class Media:
        css = {
            'all': ('//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.min.css', 'css/summernote.css',),
        }
        js = ('js/summernote.min.js', 'js/jquery.summernote-django.js',)

    def __init__(self, attrs=None):
        default_attrs = self.custom_attrs.copy()
        if attrs:
            default_attrs.update(attrs)
        super(Textarea, self).__init__(default_attrs)
