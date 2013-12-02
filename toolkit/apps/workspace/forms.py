# -*- coding: utf-8 -*-
from django import forms

from parsley.decorators import parsleyfy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div

from toolkit.apps.workspace.services import EnsureCustomerService

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


@parsleyfy
class AddWorkspaceTeamMemberForm(forms.Form):
    client_full_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs = {'placeholder': 'Client Full Name', 'size': '40'})
    )
    client_email_address = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs = {'placeholder': 'Email address', 'size': '40'})
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # remove the instance
        self.workspace = kwargs.pop('workspace')

        self.helper = FormHelper()
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            Div(
                'client_full_name',
                'client_email_address',
                css_class='form-inline'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )

        super(AddWorkspaceTeamMemberForm, self).__init__(*args, **kwargs)

    def clean_client_email_address(self):
        email = self.cleaned_data.get('client_email_address')
        if email in [u.email for u in self.workspace.participants.all()]:
            raise forms.ValidationError('User "%s" is already part of the team' % email)
        return email

    def save(self):
        customer_service = EnsureCustomerService(email=self.cleaned_data.get('client_email_address'),
                                                 full_name=self.cleaned_data.get('client_full_name'))
        customer_service.process()
        user = customer_service.user
        is_new = customer_service.is_new

        return user, is_new

