# -*- coding: utf-8 -*-
from django import forms

from parsley.decorators import parsleyfy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from .models import EightyThreeB


@parsleyfy
class EightyThreeBForm(forms.Form):
    client_full_name = forms.CharField()
    client_email_address = forms.EmailField()
    workspace = forms.CharField(label='Company Name')
    post_code = forms.CharField()
    state = forms.CharField()
    address = forms.CharField()
    date_of_property_transfer = forms.DateField()
    description = forms.CharField()
    tax_year = forms.CharField()
    value_at_time_of_transfer = forms.CharField()
    ssn = forms.CharField()
    itin = forms.CharField()
    accountant_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
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
                Submit('submit', 'Submit', css_class='button white')
            )
        )
        super(EightyThreeBForm, self).__init__(*args, **kwargs)