# -*- coding: utf-8 -*-
from django import forms

from parsley.decorators import parsleyfy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit


@parsleyfy
class SignUpForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'email',
            'password',
            'password_confirm',
            ButtonHolder(
                Submit('submit', 'Signup', css_class='button white')
            )
        )
        super(SignUpForm, self).__init__(*args, **kwargs)


@parsleyfy
class SignInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'email',
            'password',
            ButtonHolder(
                Submit('submit', 'Login', css_class='button white')
            )
        )
        super(SignInForm, self).__init__(*args, **kwargs)


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
