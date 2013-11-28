# -*- coding: utf-8 -*-
from django import forms

from localflavor.us.forms import USZipCodeField, USSocialSecurityNumberField
from localflavor.us.us_states import USPS_CHOICES

from parsley.decorators import parsleyfy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from toolkit.apps.workspace.services import EnsureCustomerService

import datetime


def _current_year():
    return datetime.datetime.utcnow().year


@parsleyfy
class EightyThreeBForm(forms.Form):
    client_full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'John Smith'}))
    client_email_address = forms.EmailField()
    post_code = USZipCodeField()
    state = forms.ChoiceField(choices=USPS_CHOICES)
    address = forms.CharField(widget=forms.Textarea)
    date_of_property_transfer = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    description = forms.CharField(widget=forms.Textarea)
    tax_year = forms.IntegerField(initial=_current_year)
    value_at_time_of_transfer = forms.DecimalField(initial=0.00)
    ssn = USSocialSecurityNumberField(required=False)
    itin = forms.CharField(required=False)
    accountant_email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance')  # pop this as we are not using a model form

        self.workspace = kwargs.pop('workspace')

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.attrs = {'data-validate': 'parsley'}

        self.helper.layout = Layout(
            'client_full_name',
            'client_email_address',
            'client_company_name',
            'post_code',
            'state',
            'address',
            'date_of_property_transfer',
            'description',
            'tax_year',
            'value_at_time_of_transfer',
            'ssn',
            'itin',
            'accountant_email',
            ButtonHolder(
                Submit('submit', 'Submit', css_class='btn-primary')
            )
        )
        super(EightyThreeBForm, self).__init__(*args, **kwargs)

    def clean_ssn(self):
        """
        if the itin is not specified and we have a blank value
        """
        ssn = self.cleaned_data.get('ssn') 
        itin = self.data.get('itin')
        if ssn in ['', None] and itin in ['', None]:
            raise forms.ValidationError("Please specify either an SSN or an ITIN")
        return ssn

    def clean_itin(self):
        """
        if the ssn is not specified and we have a blank value
        """
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

