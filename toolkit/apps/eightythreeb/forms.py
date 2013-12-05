# -*- coding: utf-8 -*-
from django import forms

from localflavor.us.forms import USZipCodeField, USSocialSecurityNumberField
from localflavor.us.us_states import USPS_CHOICES

from parsley.decorators import parsleyfy

from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import HTML, Div, Field, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import PrependedText, FieldWithButtons, StrictButton

from toolkit.apps.workspace.services import EnsureCustomerService

from .signals import lawyer_complete_form, customer_complete_form

import datetime


def _current_year():
    return datetime.datetime.utcnow().year


LAWYER_LAYOUT = Layout(
    Fieldset(
        '',
        HTML('<label class="control-label">Client Details</label>'),
        Div(
            'client_full_name',
            'client_email',
            css_class='form-inline'
        ),
    ),
    Fieldset(
        '83b Election Information',
        FieldWithButtons(
            'date_of_property_transfer',
            StrictButton('<span class="fui-calendar"></span>'),
            css_class='datetime'
        ),
        'description',
        'tax_year',
        'nature_of_restrictions',
        Div(
            HTML('<label class="control-label">Value at time of transfer</label>'),
            Div(
                PrependedText('transfer_value_share', '$'),
                HTML('<span class="help-block">per share for a total aggregate value of</span>'),
                PrependedText('transfer_value_total', '$'),
                css_class='form-inline'
            ),
            css_class='form-group'
        ),
        Div(
            HTML('<legend>Additional Details (Client to complete)</legend>'),
            Field('state', disabled='disabled'),
            Div(
                Field('ssn', readonly='readonly'),
                HTML('<span class="help-block">or</span>'),
                Field('itin', readonly='readonly'),
                css_class='form-inline'
            ),
            Field('accountant_email', readonly='readonly'),
            css_class='dialog dialog-success form-dialog'
        )
    ),
    ButtonHolder(
        Submit('submit', 'Continue', css_class='btn-hg btn-primary'),
        css_class='form-group'
    )
)


CUSTOMER_LAYOUT = Layout(
    Fieldset(
        '',
        HTML('<label class="control-label">Client Details</label>'),
        Div(
            'client_full_name',
            'client_email',
            css_class='form-inline'
        ),
        'post_code',
        'state',
        'address',
        Div(
            Div(
                'ssn',
                HTML('<span class="help-block">or</span>'),
                'itin',
                css_class='form-inline'
            ),
            HTML('<span class="help-block">This tool is currently only available to people with an SSN or ITIN number.</span>'),
            css_class='form-inline'
        ),
        'accountant_email',
    ),
    Fieldset(
        'Please confirm the following is correct',
        FieldWithButtons(
            'date_of_property_transfer',
            StrictButton('<span class="fui-calendar"></span>'),
            css_class='datetime'
        ),
        'description',
        'tax_year',
        'nature_of_restrictions',
        Div(
            HTML('<label class="control-label">Value at time of transfer</label>'),
            Div(
                PrependedText('transfer_value_share', '$'),
                HTML('<span class="help-block">per share for a total aggregate value of</span>'),
                PrependedText('transfer_value_total', '$'),
                css_class='form-inline'
            ),
            css_class='form-group'
        )
    ),
    ButtonHolder(
        Submit('submit', 'Continue', css_class='btn-hg btn-primary'),
        css_class='form-group'
    )
)


@parsleyfy
class EightyThreeBForm(forms.Form):
    client_full_name = forms.CharField(
        error_messages={
            'required': "Client name can't be blank."
        },
        help_text='',
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Client full name', 'size': '40'})
    )
    client_email = forms.EmailField(
        error_messages={
            'invalid': "Client email is invalid.",
            'required': "Client email can't be blank."
        },
        help_text='',
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Client email address', 'size': '40'})
    )
    post_code = USZipCodeField(
        label='Zip Code',
        required=False
    )
    state = forms.ChoiceField(
        choices=USPS_CHOICES,
        label='Where do you live?',
        help_text='The state where you file your taxes',
        initial='CA',
        required=False
    )
    address=forms.CharField(
        label='Address',
        widget=forms.Textarea,
        required=False
    )
    ssn = USSocialSecurityNumberField(
        label='Social Security Number',
        required=False
    )
    itin = forms.CharField(
        label='Tax Payer ITIN',
        required=False
    )
    accountant_email = forms.EmailField(
        label='Your accountants email address',
        required=False
    )
    date_of_property_transfer = forms.DateField(
        error_messages={
            'invalid': "Property transfer date is invalid.",
            'required': "Property transfer date can't be blank."
        },
        help_text='The filing deadline is 30 days from this date. Your filing deadline is June 24th 2013.',
        input_formats=['%B %d, %Y'],
        label='Date on which the property was transferred',
        widget=forms.DateInput(attrs={'class': 'datepicker'}, format=['%B %d, %Y'])
    )
    description = forms.CharField(
        error_messages={
            'required': "Property description can't be blank."
        },
        label='Description of property with respect to which election is being made',
        help_text='e.g. 10 shares of the common stock of ABC, Inc ($0.0001 per value)',
        widget=forms.Textarea(attrs={'cols': '80'})
    )
    tax_year = forms.IntegerField(
        error_messages={
            'required': "Tax year can't be blank."
        },
        label='Taxable year for which the election is being made',
        initial=_current_year,
        widget=forms.NumberInput(attrs={'size': '4'})
    )
    nature_of_restrictions = forms.CharField(
        error_messages={
            'required': "Nature of restrictions can't be blank."
        },
        label='Nature of restrictions to which property is subject',
        help_text='If you have copied this from Microsoft Word then please check the numbering and formatting has been retained.',
        widget=forms.Textarea(attrs={'cols': '80'})
    )
    transfer_value_share = forms.DecimalField(
        error_messages={
            'required': "Transfer value per share can't be blank."
        },
        label='',
        initial=0.00,
        widget=forms.TextInput(attrs={'size': '10'})
    )
    transfer_value_total = forms.DecimalField(
        error_messages={
            'required': "Transfer value total can't be blank."
        },
        label='',
        initial=0.00,
        widget=forms.TextInput(attrs={'size': '10'})
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        self.user = None
        if request is not None:
            self.user = request.user

        kwargs.pop('instance')  # pop this as we are not using a model form

        self.workspace = kwargs.pop('workspace')

        self.helper = FormHelper()
        self.helper.attrs = {
            'parsley-validate': '',
            'parsley-error-container': '.parsley-errors'
        }
        self.helper.form_show_errors = False

        self.helper.layout = LAWYER_LAYOUT if self.user.profile.is_lawyer else CUSTOMER_LAYOUT

        super(EightyThreeBForm, self).__init__(*args, **kwargs)

        # sync the fields with the appropriate user layout
        helper_fields = [field_name for pos, field_name in self.helper.layout.get_field_names()]
        for field_name in self.fields.keys():
            if field_name not in helper_fields:
                del self.fields[field_name]

    def clean_date_of_property_transfer(self):
        date = self.cleaned_data.get('date_of_property_transfer')

        if date < (datetime.date.today() - datetime.timedelta(days=25)):
            raise forms.ValidationError('This requires a minimum of 5 days to complete the election')

        return date

    def clean_ssn(self):
        """
        if the itin is not specified and we have a blank value
        """
        if self.user.profile.is_customer:
            if 'ssn' in self.fields:
                ssn = self.cleaned_data.get('ssn')
                itin = self.data.get('itin')
                if ssn in ['', None] and itin in ['', None]:
                    raise forms.ValidationError("Please specify either an SSN or an ITIN")
                return ssn

    def clean_itin(self):
        """
        if the ssn is not specified and we have a blank value
        """
        if self.user.profile.is_customer:
            if 'itin' in self.fields:
                itin = self.cleaned_data.get('itin')
                ssn = self.data.get('ssn')
                if ssn in ['', None] and itin in ['', None]:
                    raise forms.ValidationError("Please specify either an SSN or an ITIN")
                return itin

    def issue_signals(self, instance):
        if self.user.profile.is_lawyer:
            lawyer_complete_form.send(sender=self.user, instance=instance, actor_name=self.user.email)

        elif self.user.profile.is_customer:
            customer_complete_form.send(sender=self.user, instance=instance, actor_name=self.user.email)

    def save(self):
        """
        Ensure we have a customer with this info
        """
        customer_service = EnsureCustomerService(email=self.cleaned_data.get('client_email'),
                                                 full_name=self.cleaned_data.get('client_full_name'))
        customer_service.process()
        user = customer_service.user
        is_new = customer_service.is_new

        eightythreeb, is_new = user.eightythreeb_set.get_or_create(workspace=self.workspace, user=user)
        eightythreeb.data.update(**self.cleaned_data)  # update the data
        eightythreeb.workspace = self.workspace
        eightythreeb.save()

        self.issue_signals(instance=eightythreeb)

        return eightythreeb
