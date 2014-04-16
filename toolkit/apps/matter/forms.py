import json

from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field, Layout

from parsley.decorators import parsleyfy

from toolkit.apps.workspace.models import Workspace
from toolkit.core.client.models import Client
from toolkit.mixins import ModalForm

from .services import MatterCloneService


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

    template = forms.ModelChoiceField(
        help_text='',
        label='Copy checklist items from',
        queryset=Workspace.objects.none(),
        required=False
    )

    class Meta:
        fields = ['matter_code', 'name']
        model = Workspace

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_new = kwargs.pop('is_new', True)

        super(MatterForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
            'name',
            'client_name',
            'matter_code',
            Field('template', css_class='select-block') if self.is_new is True else None
        )

        # Only show matters that I'm a participant in
        self.fields['template'].queryset = Workspace.objects.mine(self.user)

        if self.instance.pk:
            if self.instance.is_archived:

                self.helper.inputs.insert(0, self.get_delete_button())
                self.helper.inputs.insert(1, Button('unarchive', 'Unarchive', css_class='btn btn-info pull-left', **{
                    'data-dismiss': 'modal',
                    'data-remote': reverse('matter:unarchive', kwargs={'matter_slug': self.instance.slug}),
                    'data-target': '#matter-unarchive-%s' % self.instance.slug,
                    'data-toggle': 'modal',
                }))

            else:
                self.helper.inputs.insert(0, Button('archive', 'Archive', css_class='btn btn-info pull-left', **{
                    'data-dismiss': 'modal',
                    'data-remote': reverse('matter:archive', kwargs={'matter_slug': self.instance.slug}),
                    'data-target': '#matter-archive-%s' % self.instance.slug,
                    'data-toggle': 'modal',
                }))


        if self.instance.client:
            self.initial['client_name'] = self.instance.client.name

        # Show all the available clients to the user
        data = json.dumps(list(Client.objects.mine(self.user).values_list('name', flat=True)))
        self.fields['client_name'].widget.attrs.update({
            'data-source': data
        })

        # Only show matters that I'm a participant in
        self.fields['template'].queryset = Workspace.objects.mine(self.user)

    def get_delete_button(self):
        if self.user_can_modify is True:
            return self.delete_button

        return self.stop_participating_button

    @property
    def show_action(self):
        """
        property to overide the ModalForm mixin test
        """
        return self.user_can_modify

    @property
    def user_can_modify(self):
        return (self.user == self.instance.lawyer or self.user.profile.is_lawyer is True and self.is_new is True)

    @property
    def delete_button(self):
        return Button('delete', 'Delete', css_class='btn btn-danger pull-left', **{
                      'data-dismiss': 'modal',
                      'data-remote': reverse('matter:delete', kwargs={'matter_slug': self.instance.slug}),
                      'data-target': '#matter-delete-%s' % self.instance.slug,
                      'data-toggle': 'modal',
                })

    @property
    def stop_participating_button(self):
        return Button('stop-participating', 'Stop Participating', css_class='btn btn-warning pull-left', **{
                      'data-dismiss': 'modal',
                      'data-remote': reverse('matter:delete', kwargs={'matter_slug': self.instance.slug}),
                      'data-target': '#matter-delete-%s' % self.instance.slug,
                      'data-toggle': 'modal',
                })

    def save(self, commit=True):
        created = True if self.instance.pk is None else False

        matter = super(MatterForm, self).save(commit=False)

        # add client/lawyer to the matter
        matter.client, is_new = self.user.clients.get_or_create(name=self.cleaned_data['client_name'])
        matter.lawyer = self.user

        matter.save()

        # add user as participant
        matter.participants.add(self.user)

        if created and self.cleaned_data['template'] is not None:
            service = MatterCloneService(source_matter=self.cleaned_data['template'], target_matter=matter)
            service.process()

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
