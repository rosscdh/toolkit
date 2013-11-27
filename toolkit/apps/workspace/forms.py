# -*- coding: utf-8 -*-
from django import forms

from parsley.decorators import parsleyfy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from .models import Workspace


@parsleyfy
class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'name',
            'users',
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
        super(WorkspaceForm, self).__init__(*args, **kwargs)