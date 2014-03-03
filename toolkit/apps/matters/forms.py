from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from parsley.decorators import parsleyfy

from toolkit.apps.workspace.models import Workspace
from toolkit.mixins import ModalForm


@parsleyfy
class MatterForm(ModalForm, forms.ModelForm):
    title = 'Create a new Matter'

    class Meta:
        model = Workspace

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = reverse('matter:create')

        self.helper.layout = Layout()

        super(MatterForm, self).__init__(*args, **kwargs)
