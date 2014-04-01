import json

from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Layout

from parsley.decorators import parsleyfy

from toolkit.apps.workspace.models import Workspace
from toolkit.core.client.models import Client
from toolkit.mixins import ModalForm


@parsleyfy
class MatterForm(ModalForm, forms.ModelForm):
    client_name = forms.CharField(
        error_messages={
            'required': "Client name can not be blank."
        },
        help_text='',
        label='Client name',
        required=True,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'placeholder': 'Acme Inc',
            'size': '40',
            # Typeahead
            'data-items': '4',
            'data-provide': 'typeahead',
            'data-source': '[]'
        })
    )

    matter_code = forms.CharField(
        help_text='Matter code is optional.',
        label='Matter code',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '00001-matter-name', 'size': '40'})
    )

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
        fields = ['matter_code', 'name']
        model = Workspace

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')

        super(MatterForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
            'name',
            'client_name',
            'matter_code'
        )

        if self.instance.pk:
            self.helper.inputs.insert(0, Button('delete', 'Delete', css_class='btn btn-danger pull-left', **{
                'data-dismiss': 'modal',
                'data-remote': reverse('matter:delete', kwargs={'matter_slug': self.instance.slug}),
                'data-target': '#matter-delete-%s' % self.instance.slug,
                'data-toggle': 'modal',
            }))

        if self.instance.client:
            self.initial['client_name'] = self.instance.client.name

        # Show all the available clients to the user
        data = json.dumps(list(Client.objects.mine(self.user).values_list('name', flat=True)))
        self.fields['client_name'].widget.attrs.update({
            'data-source': data
        })

    def save(self, commit=True):
        matter = super(MatterForm, self).save(commit=False)

        # add client/lawyer to the matter
        matter.client, is_new = self.user.clients.get_or_create(name=self.cleaned_data['client_name'])
        matter.lawyer = self.user

        matter.save()

        # add user as participant
        matter.participants.add(self.user)

        return matter

    @property
    def action_url(self):
        if self.instance.pk:
            return reverse('matter:edit', kwargs={'matter_slug': self.instance.slug})
        return reverse('matter:create')

    @property
    def title(self):
        if self.instance.pk:
            return 'Update: %s' % self.instance.name
        return 'Create a new Matter'
