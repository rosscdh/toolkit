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

    name = forms.CharField(
        error_messages={
            'required': "Matter name can not be blank."
        },
        help_text='',
        label='Matter name',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Matter name', 'size': '40'})
    )

    class Meta:
        fields = ['name']
        model = Workspace

    def __init__(self, user, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = reverse('matter:create')

        self.helper.layout = Layout(
            'name',
        )

        self.user = user

        super(MatterForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        matter = super(MatterForm, self).save(commit=commit)

        # add lawyer
        matter.lawyer = self.user
        matter.save(update_fields=['lawyer'])

        # add user as participant
        matter.participants.add(self.user)

        return matter
