# -*- coding: utf-8 -*-
from django import forms

from localflavor.us.forms import USZipCodeField, USSocialSecurityNumberField
from localflavor.us.us_states import USPS_CHOICES

from parsley.decorators import parsleyfy

from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *

from toolkit.apps.workspace.services import EnsureCustomerService

import datetime


def _current_year():
    return datetime.datetime.utcnow().year


LAWYER_LAYOUT = Layout(
    Fieldset(
        '',
        HTML('<label class="control-label">Client Details</label>'),
        Div(
            'client_full_name',
            'client_email_address',
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
            'client_email_address',
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
        label  = '',
        widget = forms.TextInput(attrs = { 'placeholder': 'Client Full Name', 'size': '40' })
    )
    client_email_address = forms.EmailField(
        label  = '',
        widget = forms.TextInput(attrs = { 'placeholder': 'Email address', 'size': '40' })
    )
    post_code = USZipCodeField(
        label = 'Zip Code'
    )
    state = forms.ChoiceField(
        choices   = USPS_CHOICES,
        label     = 'Where do you live?',
        help_text = 'The state where you file your taxes'
    )
    address = forms.CharField(
        widget = forms.Textarea
    )
    date_of_property_transfer = forms.DateField(
        input_formats = ['%Y-%m-%d', '%d %B, %Y'],
        label         = 'Date on which the property was transferred',
        help_text     = 'The filing deadline is 30 days from this date. Your filing deadline is June 24th 2013.',
        widget        = forms.TextInput(attrs = { 'class': 'datepicker' })
    )
    description = forms.CharField(
        label     = 'Description of property with respect to which election is being made',
        help_text = 'e.g. 10 shares of the common stock of ABC, Inc ($0.0001 per value)',
        widget    = forms.Textarea(attrs = { 'cols': '80' })
    )
    tax_year = forms.IntegerField(
        label   = 'Taxable year for which the election is being made',
        initial = _current_year,
        widget  = forms.NumberInput(attrs = { 'size': '4' })
    )
    nature_of_restrictions = forms.CharField(
        label     = 'Nature of restrictions to which property is subject',
        help_text = 'If you have copied this from Microsoft Word then please check the numbering and formatting has been retained.',
        widget    = forms.Textarea(attrs = { 'cols': '80' })
    )
    transfer_value_share = forms.DecimalField(
        label   = '',
        initial = 0.00,
        widget  = forms.TextInput(attrs = { 'size': '10' })
    )
    transfer_value_total = forms.DecimalField(
        label   = '',
        initial = 0.00,
        widget  = forms.TextInput(attrs = { 'size': '10' })
    )
    ssn = USSocialSecurityNumberField(
        label    = 'Social Security Number',
        required = False
    )
    itin = forms.CharField(
        label    = 'Tax Payer ITIN',
        required = False
    )
    accountant_email = forms.EmailField(
        label     = 'Your accountants email address',
        required  = False
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        user = None
        if request is not None:
            user = request.user

        instance = kwargs.pop('instance')  # pop this as we are not using a model form

        self.workspace = kwargs.pop('workspace')

        self.helper = FormHelper()
        self.helper.attrs = { 'data-validate': 'parsley' }

        self.helper.layout = LAWYER_LAYOUT if user.profile.is_lawyer else CUSTOMER_LAYOUT

        super(EightyThreeBForm, self).__init__(*args, **kwargs)

        # sync the fields with the appropriate user layout
        # for f in self.fields.keys():
            # if f not in self.helper.layout.fields:
                # del self.fields[f]

    def clean_ssn(self):
        """
        if the itin is not specified and we have a blank value
        """
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
        if 'itin' in self.fields:
            itin = self.cleaned_data.get('itin') 
            ssn = self.data.get('ssn')
            if ssn in ['', None] and itin in ['', None]:
                raise forms.ValidationError("Please specify either an SSN or an ITIN")
            return itin

    def save(self):
        """
        Ensure we have a customer with this info
        """
        customer_service = EnsureCustomerService(email=self.cleaned_data.get('client_email_address'),
                                                 full_name=self.cleaned_data.get('client_full_name'))
        customer_service.process()
        user = customer_service.user
        is_new = customer_service.is_new

        eightythreeb, is_new = user.eightythreeb_set.get_or_create(workspace=self.workspace, user=user)
        eightythreeb.data.update(**self.cleaned_data)  # update the data
        eightythreeb.workspace = self.workspace
        eightythreeb.save()

        return eightythreeb
