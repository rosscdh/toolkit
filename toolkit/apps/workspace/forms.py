# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.template.defaultfilters import slugify

from parsley.decorators import parsleyfy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div

from toolkit.apps.workspace.services import EnsureCustomerService
from toolkit.apps.workspace.models import InviteKey

from .models import Workspace
from .mailers import InviteUserToToolEmail

from toolkit.mixins import FormModal


@parsleyfy
class WorkspaceForm(FormModal, forms.ModelForm):
    name = forms.CharField(
        error_messages={
            'required': "Company name can't be blank."
        },
        label='Company name',
        widget=forms.TextInput(attrs={'size': '40'})
    )

    class Meta:
        model = Workspace

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = reverse('workspace:create')

        self.helper.layout = Layout(
            'name',
        )

        super(WorkspaceForm, self).__init__(*args, **kwargs)


@parsleyfy
class AddWorkspaceTeamMemberForm(FormModal, forms.Form):
    client_full_name = forms.CharField(
        error_messages={
            'required': "Client name can't be blank."
        },
        widget=forms.TextInput(attrs={'placeholder': 'Full name', 'size': '40'})
    )
    client_email_address = forms.EmailField(
        error_messages={
            'invalid': "Client email is invalid.",
            'required': "Client name can't be blank."
        },
        widget=forms.TextInput(attrs={'placeholder': 'Email', 'size': '40'})
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # remove the instance
        self.workspace = kwargs.pop('workspace')

        self.helper = FormHelper()
        self.helper.form_action = reverse('workspace:add_team_member', args=(self.workspace.slug,))

        self.helper.layout = Layout(
            'client_full_name',
            'client_email_address'
        )

        super(AddWorkspaceTeamMemberForm, self).__init__(*args, **kwargs)

    def clean_client_email_address(self):
        email = self.cleaned_data.get('client_email_address')
        if email in [u.email for u in self.workspace.participants.all()]:
            raise forms.ValidationError('"%s" is already part of the team' % email)
        return email

    def save(self):
        customer_service = EnsureCustomerService(email=self.cleaned_data.get('client_email_address'),
                                                 full_name=self.cleaned_data.get('client_full_name'))
        customer_service.process()
        user = customer_service.user
        is_new = customer_service.is_new

        return user, is_new


@parsleyfy
class InviteUserForm(forms.Form):
    subject = forms.CharField(
         widget=forms.TextInput(attrs={'size':'45'})
    )
    message = forms.CharField(widget=forms.Textarea(attrs={
            'cols': '80',
            'data-toggle': 'summernote'
        }))

    def __init__(self, *args, **kwargs):
        self.key_instance = kwargs.pop('key_instance', None)
        self.tool_instance = kwargs.pop('tool_instance', None)
        self.instance = kwargs.pop('instance', None)
        self.request = kwargs.pop('request', None)
        self.user = getattr(self.request, 'user', None)

        self.helper = FormHelper()
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'subject',
            'message',
            ButtonHolder(
                Submit('submit', 'Send Invite', css_class='btn-lg white')
            )

        )
        super(InviteUserForm, self).__init__(*args, **kwargs)
        self.fields['subject'].initial = self.get_initial_subject()
        self.fields['message'].initial = self.get_initial_message()

    def get_initial_subject(self):
        template = get_template('%s/invite_subject.html' % slugify(self.tool_instance._meta.model.__name__))
        return template.render(Context({'request': self.request, 'instance': self.tool_instance, 'user': self.user}))

    def get_initial_message(self):
        template = get_template('%s/invite_message.html' % slugify(self.tool_instance._meta.model.__name__))
        return template.render(Context({'request': self.request,
                                        'instance': self.tool_instance,
                                        'user': self.user,
                                        '83b_action_url': '%s' % self.key_instance.get_invite_login_url(request=self.request)
                                        }))
    def save(self, **kwargs):
        """
        Mock save (as were not using an forms.ModelForm)
        this allows us to send the email as part of the form
        NB! the InviteKey object is created by the view
        """
        m = InviteUserToToolEmail(subject=self.cleaned_data.get('subject'),
                                  message=self.cleaned_data.get('message'),
                                  from_tuple=(self.user.get_full_name(), self.user.email),
                                  recipients=((self.tool_instance.user.get_full_name(), self.tool_instance.user.email),))
        m.process()



@parsleyfy
class InviteKeyForm(forms.Form):
    invite_key = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'invite_key',
            ButtonHolder(
                Submit('submit', 'Login', css_class='button white')
            )
        )
        super(InviteKeyForm, self).__init__(*args, **kwargs)

    def clean_invite_key(self):
        key = self.cleaned_data['invite_key']
        try:
            InviteKey.objects.get(key=key)

        except InviteKey.DoesNotExist:
            raise forms.ValidationError('Sorry, that key does not exist.')
