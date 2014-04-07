# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse_lazy

from parsley.decorators import parsleyfy
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import ButtonHolder, Div, Field, Fieldset, HTML, Submit

from . import _get_unique_username
from toolkit.core.services.analytics import AtticusFinch

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
        widget=forms.TextInput(attrs={'placeholder': 'Firm name'})
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
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'autocomplete':'off'})
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
        widget=forms.PasswordInput(attrs={'placeholder': 'Password again'})
    )
    t_and_c = forms.BooleanField(
        error_messages={
            'required': "You must agree to the LawPal Terms and Conditions."
        },
        initial=False,
        label='I agree to the LawPal Terms and Conditions.',
        required=True
    )

    mpid = forms.CharField(
        label='',
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {
            'id': 'signup-form',
            'parsley-validate': ''
        }
        self.helper.form_show_errors = False

        self.helper.layout = Layout(
            HTML('{% include "partials/form-errors.html" with form=form %}'),
            Fieldset(
                '',
                Field('firm_name'),
                Div(
                    Field('first_name', css_class=''),
                    Field('last_name', css_class=''),
                    css_class='form-name clearfix'
                ),

                Field('email'),
                Field('password'),
                Field('password_confirm'),
                Field('t_and_c', template='public/bootstrap3/t_and_c.html'),
                Field('mpid'),
            ),
            ButtonHolder(
                Submit('submit', 'Create Account')
            )
        )

        super(SignUpForm, self).__init__(*args, **kwargs)

        # Override the label with a link to the terms (can't go higher as the urls aren't loaded yet)
        self.fields['t_and_c'].label = 'I agree to the LawPal <a href="%s" target="_blank">Terms and Conditions</a>.' % reverse_lazy('public:terms')

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
        """
        Ensure the email is normalised
        """
        email = User.objects.normalize_email(self.cleaned_data.get('email'))
        user = User.objects.filter(email=email).first()

        if user is None:
            return email
        else:
            raise forms.ValidationError("An account with that email already exists.")

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

        mpid = self.cleaned_data.get('mpid', None)

        analytics = AtticusFinch()
        if mpid not in ['', None]:
            analytics.mixpanel_alias(user.pk, mpid)
        analytics.event('user.signup', user=user)

        return user


@parsleyfy
class SignInForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            'required': "Email can't be blank."
        },
        label='',
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'})
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
                Submit('submit', 'Secure Sign In', css_class='btn btn-primary btn-lg')
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
