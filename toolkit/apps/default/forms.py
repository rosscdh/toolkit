# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from parsley.decorators import parsleyfy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, Fieldset

from . import _get_unique_username

import logging
LOGGER = logging.getLogger('django.request')


@parsleyfy
class SignUpForm(forms.Form):
    username = forms.CharField(required=False, widget=forms.HiddenInput)
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email address', 'class': 'input-lg'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-lg'}))
    password_confirm = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password again', 'class': 'input-lg'}))
    t_and_c = forms.BooleanField(label='I agree to the LawPal Terms and Conditions', required=True, initial=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('email', css_class='input-hg'),
                Field('password', css_class='input-hg'),
                Field('password_confirm', css_class='input-hg'),
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
            raise forms.ValidationError('Passwords do not match')

        return password_confirm

    def clean_email(self):
        email = self.cleaned_data.get('email')

        try:
            user = User.objects.get(email=email)

            if user:
                raise forms.ValidationError("Email already Exists. Please use another")

        except User.DoesNotExist:
            return email

    def save(self):
        user = User.objects.create_user(self.cleaned_data.get('username'),
                                        self.cleaned_data.get('email'),
                                        self.cleaned_data.get('password'))
        # save the lawyer profile
        profile = user.profile
        profile.data['user_class'] = 'lawyer'
        profile.save(update_fields=['data'])

        return user


@parsleyfy
class SignInForm(forms.Form):
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email address', 'class': 'input-lg'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-lg'}))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
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
            raise forms.ValidationError("Sorry, no account with those credentials was found")

        return super(SignInForm, self).clean()
