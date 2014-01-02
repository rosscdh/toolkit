# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from parsley.decorators import parsleyfy
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import ButtonHolder, Div, Field, Fieldset, HTML, Submit

from . import _get_unique_username

import logging
LOGGER = logging.getLogger('django.request')


@parsleyfy
class SignUpForm(forms.Form):
    username = forms.CharField(
        required=False,
        widget=forms.HiddenInput
    )
    firm_name = forms.CharField(
        error_messages={
            'required': "Firm name can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Firm name', 'size': 46})
    )
    first_name = forms.CharField(
        error_messages={
            'required': "First name can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        error_messages={
            'required': "Last name can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        error_messages={
            'invalid': "Email is invalid.",
            'required': "Email can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Email address', 'size': 46})
    )
    password = forms.CharField(
        error_messages={
            'required': "Password can't be blank."
        },
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password_confirm = forms.CharField(
        error_messages={
            'required': "Confirm password can't be blank."
        },
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password confirmation'})
    )
    t_and_c = forms.BooleanField(
        error_messages={
            'required': "You must agree to the LawPal Terms and Conditions."
        },
        initial=False,
        label='I agree to the LawPal Terms and Conditions',
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {
            'parsley-validate': ''
        }
        self.helper.form_show_errors = False

        self.helper.layout = Layout(
            HTML('{% include "partials/form-errors.html" with form=form %}'),
            Fieldset(
                '',
                Field('firm_name', css_class='input-hg'),
                Div(
                    Field('first_name', css_class='input-hg'),
                    Field('last_name', css_class='input-hg'),
                    css_class='form-inline'
                ),
                Field('email', css_class='input-hg'),
                Div(
                    Field('password', css_class='input-hg'),
                    Field('password_confirm', css_class='input-hg'),
                    css_class='form-inline'
                ),
                Field('t_and_c', template='public/bootstrap3/t_and_c.html'),
            ),
            ButtonHolder(
                Submit('submit', 'Create my account', css_class='btn btn-primary btn-lg')
            )
        )

        super(SignUpForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        final_username = self.data.get('email').split('@')[0]

        final_username = _get_unique_username(username=final_username)

        LOGGER.info('Username %s available' % final_username)
        return final_username

    def clean_password_confirm(self):
        password_confirm = self.cleaned_data.get('password_confirm')
        password = self.cleaned_data.get('password')

        if password != password_confirm:
            raise forms.ValidationError("The two password fields didn't match.")

        return password_confirm

    def clean_email(self):
        email = self.cleaned_data.get('email')

        try:
            user = User.objects.get(email=email)

            if user:
                raise forms.ValidationError("An account with that email already exists.")

        except User.DoesNotExist:
            return email

    def save(self):
        user = User.objects.create_user(self.cleaned_data.get('username'),
                                        self.cleaned_data.get('email'),
                                        self.cleaned_data.get('password'),
                                        first_name=self.cleaned_data.get('first_name'),
                                        last_name=self.cleaned_data.get('last_name'))

        # save the lawyer profile
        profile = user.profile
        profile.data['firm_name'] = self.cleaned_data.get('firm_name')
        profile.data['user_class'] = profile.LAWYER
        profile.save(update_fields=['data'])

        return user


@parsleyfy
class SignInForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            'required': "Email can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Email address'})
    )
    password = forms.CharField(
        error_messages={
            'required': "Password can't be blank."
        },
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

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
                Field('email', css_class='input-hg'),
                Field('password', css_class='input-hg'),
            ),
            ButtonHolder(
                Submit('submit', 'Sign in', css_class='btn btn-primary btn-lg')
            )
        )
        super(SignInForm, self).__init__(*args, **kwargs)

    def clean(self):
        user = None
        if 'email' in self.cleaned_data and 'password' in self.cleaned_data:
            user = authenticate(username=self.cleaned_data['email'], password=self.cleaned_data['password'])

        if user is None:
            raise forms.ValidationError("Sorry, no account with those credentials was found.")

        return super(SignInForm, self).clean()
