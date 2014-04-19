# -*- coding: utf-8 -*-
from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.contrib.auth.forms import SetPasswordForm

from django.contrib.auth.hashers import make_password

import os

from storages.backends.s3boto import S3BotoStorage

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Field, Fieldset, HTML, Layout, Submit

from parsley.decorators import parsleyfy

from toolkit.apps.default.fields import HTMLField
from toolkit.mixins import ModalForm

from .mailers import (ValidatePasswordChangeMailer, ValidateEmailChangeMailer)

import logging
logger = logging.getLogger('django.request')


User = get_user_model()


class BaseAccountSettingsFields(object):
    """
    Provides base field for various account settings forms
    """
    first_name = forms.CharField(
        error_messages={
            'required': "First name can't be blank."
        },
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'First name', 'size': 15})
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
        widget=forms.EmailInput(attrs={'placeholder': 'example@lawpal.com', 'size': 44})
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
                Div(
                    HTML('<label>Full name<span class="asteriskField">*</span></label>'),
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
                Submit('submit', 'Save changes', css_class='btn btn-primary btn-lg'),
                css_class='form-group'
            )
        )

        super(BaseAccountSettingsFields, self).__init__(*args, **kwargs)

@parsleyfy
class AccountSettingsForm(BaseAccountSettingsFields, forms.ModelForm):

    class Meta:
        fields = ('first_name', 'last_name', 'email')
        model = User

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = self.request.user

        super(AccountSettingsForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        save the requested email in the user.profile.data['validation_required_temp_email']
        send the confirmation email
        on reciept of the confirmation link click update the user email
        """
        profile = self.user.profile
        # salt and hash this thing
        temp_email = self.cleaned_data['email']

        # @TODO turn this into a reuseable function as its used in SignupForm too
        temp_email = User.objects.normalize_email(self.cleaned_data.get('email'))
        existing_user = User.objects.filter(email=temp_email).first()

        if existing_user is not None:
            raise forms.ValidationError("An account with that email already exists.")

        # detect a change
        if temp_email != self.user.email:
            profile.data['validation_required_temp_email'] = temp_email
            # require them to validate their email
            profile.validated_email = False
            profile.save(update_fields=['data'])

            m = ValidateEmailChangeMailer(
                    recipients=((self.user.get_full_name(), self.user.email),),)
            m.process(user=self.user)

            messages.warning(self.request, 'For your security you have been logged out. Please check your email address "%s" and click the email address change confirmation validation link' % self.request.user.email)
            logger.info('User: %s has requested a change of email address' % self.user)

            logout(self.request)

            # always return the current email address! we dotn want to change it
            # until the change has been confirmed
        return self.user.email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name != self.user.first_name:
            messages.success(self.request, 'Success. You have updated your First Name')
            return first_name
        return self.user.first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name != self.user.last_name:
            messages.success(self.request, 'Success. You have updated your Last Name')
            return last_name
        return self.user.last_name


@parsleyfy
class ConfirmAccountForm(BaseAccountSettingsFields, forms.ModelForm):
    """
    Signup Form
    """
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

    class Meta:
        fields = ('first_name', 'last_name', 'email')
        model = User

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
                Submit('submit', 'Continue', css_class='btn btn-primary btn-lg'),
                css_class='form-group'
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
class ChangePasswordForm(ModalForm, SetPasswordForm):
    title = "Change your password"

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
        self.request = kwargs.pop('request', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('new_password1', css_class='input-hg'),
                Field('new_password2', css_class='input-hg'),
            )
        )

    @property
    def action_url(self):
        return reverse('me:change-password')

    def clean_new_password2(self):
        """
        save the password salted and hashed in user.profile
        send the confirmation email
        on reciept of the confirmation link click only then update the user password
        """
        profile = self.user.profile

        new_password = self.cleaned_data['new_password2']

        # salt and hash this thing for comparison
        temp_password = make_password(new_password)

        profile.data['validation_required_temp_password'] = temp_password
        profile.save(update_fields=['data'])

        # send confirmation email
        m = ValidatePasswordChangeMailer(recipients=((self.user.get_full_name(), self.user.email),),)
        m.process(user=self.user)

        messages.warning(self.request, 'For your security you have been logged out. Please check your email address "%s" and click the change of password confirmation validation link' % self.request.user.email)
        logger.info('User: %s has requested a change of password' % self.user)

        logout(self.request)

        return new_password

    def save(self, *args, **kwargs):
        #
        # Do nothing here
        #
        pass



@parsleyfy
class LawyerLetterheadForm(forms.Form):
    """
    @TODO phase this form out; part of the original toolkit that is probably
    not going to get used
    """
    firm_name = forms.CharField(
        error_messages={
            'required': "Firm name can not be blank."
        },
        help_text='',
        label='Firm name',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Firm name', 'size': '40'})
    )

    firm_address = HTMLField(
        error_messages={
            'required': "Firm address can not be blank."
        },
        help_text='',
        label='Firm address',
        required=True
    )

    firm_logo = forms.ImageField(
        help_text='',
        label='',
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.user = kwargs.pop('user')

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                'firm_name',
                HTML('<label>Firm logo</label>'),
                Div(
                    Div(
                        HTML('{% load thumbnail %}{% thumbnail object.firm_logo "x150" crop="center" as im %}<img src="{{ im.url }}" width="{{ im.width }}" height="{{ im.height }}" class="img-thumbnail">{% endthumbnail %}'),
                        css_class='firm-logo-preview pull-left'
                    ),
                    Div(
                        'firm_logo',
                        css_class='pull-left',
                    ),
                    css_class='form-group clearfix'
                ),
                'firm_address'
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn btn-primary btn-lg'),
                css_class='form-group'
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
