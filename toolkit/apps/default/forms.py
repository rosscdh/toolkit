# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User

from parsley.decorators import parsleyfy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit


@parsleyfy
class SignUpForm(forms.Form):
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email address', 'class': 'input-lg'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-lg'}))
    password_confirm = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password again', 'class': 'input-lg'}))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'email',
            'password',
            'password_confirm',
            ButtonHolder(
                Submit('submit', 'Signup', css_class='btn btn-primary btn-lg')
            )
        )
        super(SignUpForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            user = User.objects.get(email=email)

            if user:
                raise forms.ValidationError("Email already Exists. Please use another")

        except User.DoesNotExist:
            return email

@parsleyfy
class SignInForm(forms.Form):
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email address', 'class': 'input-lg'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-lg'}))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'email',
            'password',
            ButtonHolder(
                Submit('submit', 'Login', css_class='btn btn-lg btn-default')
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
