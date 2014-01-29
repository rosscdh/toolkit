# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.contrib.auth.forms import SetPasswordForm

import os

from storages.backends.s3boto import S3BotoStorage

from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import ButtonHolder, Div, Field, Fieldset, HTML, Submit

from parsley.decorators import parsleyfy

from toolkit.mixins import ModalForm

User = get_user_model()


@parsleyfy
class AccountSettingsForm(forms.ModelForm):
    first_name = forms.CharField(
        error_messages={
            'required': "First name can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'First name', 'size': 19})
    )

    last_name = forms.CharField(
        error_messages={
            'required': "Last name can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Last name', 'size': 25})
    )

    email = forms.EmailField(
        error_messages={
            'invalid': "Email is invalid.",
            'required': "Email can't be blank."
        },
        widget=forms.EmailInput(attrs={'placeholder': 'example@lawpal.com', 'size': 50})
    )

    class Meta:
        fields = ('first_name', 'last_name', 'email')
        model = User

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {
            'parsley-validate': '',
        }
        self.helper.form_show_errors = False

        self.helper.layout = Layout(
            HTML('{% include "partials/form-errors.html" with form=form %}'),
            Fieldset(
                '',
                Div(
                    HTML('<label>Full name*</label>'),
                    Div(
                        Field('first_name', css_class='input-hg'),
                        Field('last_name', css_class='input-hg'),
                        css_class='form-inline'
                    )
                ),
                Field('email', css_class='input-hg'),
                Div(
                    HTML('<label>Password</label>'),
                    Div(
                        HTML('<a href="{% url "me:change-password" %}" data-toggle="modal" data-target="#change-password" class="btn btn-default btn-sm"> Change your password</a>'),
                    ),
                    css_class='form-group'
                )
            ),
            ButtonHolder(
                Submit('submit', 'Save changes', css_class='btn btn-primary btn-lg')
            )
        )

        super(AccountSettingsForm, self).__init__(*args, **kwargs)


@parsleyfy
class ChangePasswordForm(ModalForm, SetPasswordForm):
    new_password1 = forms.CharField(
        error_messages={
            'required': "New password can't be blank."
        },
        label='New password',
        widget=forms.PasswordInput(attrs={'size': 30})
    )

    new_password2 = forms.CharField(
        error_messages={
            'required': "Verify password can't be blank."
        },
        label='Verify password',
        widget=forms.PasswordInput(attrs={
            'parsley-equalto': '[name="new_password1"]',
            'parsley-equalto-message': "The two password fields don't match.",
            'size': 30
        })
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = reverse('me:change-password')

        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('new_password1', css_class='input-hg'),
                Field('new_password2', css_class='input-hg'),
            )
        )

        super(ChangePasswordForm, self).__init__(*args, **kwargs)


@parsleyfy
class ConfirmAccountForm(AccountSettingsForm):
    new_password1 = forms.CharField(
        error_messages={
            'required': "New password can't be blank."
        },
        label='Password',
        widget=forms.PasswordInput(attrs={'size': 30})
    )

    new_password2 = forms.CharField(
        error_messages={
            'required': "Verify password can't be blank."
        },
        label='Verify password',
        widget=forms.PasswordInput(attrs={
            'parsley-equalto': '[name="new_password1"]',
            'parsley-equalto-message': "The two password fields do not match.",
            'size': 30
        })
    )

    def __init__(self, *args, **kwargs):
        super(ConfirmAccountForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
            HTML('{% include "partials/form-errors.html" with form=form %}'),
            Fieldset(
                '',
                Div(
                    HTML('<p>Welcome to LawPal. Enter the information below to create your account.</p>')
                ),
                Div(
                    HTML('<label>Full name*</label>'),
                    Div(
                        Field('first_name', css_class='input-lg'),
                        Field('last_name', css_class='input-lg'),
                        css_class='form-inline'
                    )
                ),
                Field('email', css_class='input-lg'),
            ),
            Fieldset(
                '',
                Field('new_password1', css_class='input-lg'),
                Field('new_password2', css_class='input-lg'),
            ),
            ButtonHolder(
                Submit('submit', 'Continue', css_class='btn btn-primary btn-lg')
            )

        )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data['new_password1'])
        return super(ConfirmAccountForm, self).save(commit=commit)


@parsleyfy
class LawyerLetterheadForm(forms.Form):
    firm_name = forms.CharField(required=True)
    firm_address = forms.CharField(required=True, widget=forms.Textarea)
    firm_logo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.user = kwargs.pop('user')

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'firm_name',
                    'firm_address',
                    css_class='col-md-6'
                ),
                Div(
                    'firm_logo',
                    HTML('{% load thumbnail %}{% thumbnail object.firm_logo "210x100" crop="center" as im %}<img src="{{ im.url }}" width="{{ im.width }}" height="{{ im.height }}">{% endthumbnail %}'),
                    css_class='col-md-6'
                ),
                css_class='row'
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn btn-primary btn-lg')
            )
        )
        super(LawyerLetterheadForm, self).__init__(*args, **kwargs)

    def save(self):
        """
        Update the user profile data
        """
        profile = self.user.profile
        data = profile.data

        firm_logo = self.cleaned_data.pop('firm_logo', None)
        if firm_logo is not None:
            if hasattr(firm_logo, 'name'):
                image_storage = S3BotoStorage()
                # slugify a unique name
                name, ext = os.path.splitext(firm_logo.name)
                filename = slugify('%s-%s-%s' % (data.get('firm_name', self.user.username), self.user.pk, name))
                image_name = '%s%s' % (filename, ext)
                # save to s3
                result = image_storage.save('firms/%s' % image_name, firm_logo)
                # save to cleaned_data
                self.cleaned_data['firm_logo'] = image_storage.url(name=result)

        data.update(**self.cleaned_data)
        profile.data = data

        profile.save(update_fields=['data'])
