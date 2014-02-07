from django_bleach.forms import BleachField
from summernote.widgets import SummernoteWidget


class HTMLField(BleachField):
    def __init__(self, *args, **kwargs):
        super(HTMLField, self).__init__(*args, **kwargs)
        self.widget = SummernoteWidget()
