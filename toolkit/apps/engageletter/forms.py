# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.bootstrap import AppendedText, FieldWithButtons, PrependedText, StrictButton
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import ButtonHolder, Div, HTML, Submit

from parsley.decorators import parsleyfy

from localflavor.us.us_states import USPS_CHOICES
from localflavor.us.forms import USZipCodeField

from toolkit.apps.workspace.mixins import WorkspaceToolFormMixin
from toolkit.apps.workspace.services import EnsureCustomerService, WordService
from toolkit.fields import SummernoteField

from .models import Attachment

import logging
logger = logging.getLogger('django.request')


class BaseForm(WorkspaceToolFormMixin):
    address1 = forms.CharField(
        error_messages={
            'required': "Address can not be blank."
        },
        label='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Address Line 1', 'size': '40'})
    )

    address2 = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Address Line 2', 'size': '40'})
    )

    city = forms.CharField(
        error_messages={
            'required': "City can not be blank."
        },
        label='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'City', 'size': '40'})
    )

    state = forms.ChoiceField(
        choices=USPS_CHOICES,
        error_messages={
            'required': "State can not be blank."
        },
        label='',
        help_text='',
        initial='CA',
        required=True
    )

    post_code = USZipCodeField(
        error_messages={
            'required': "Zip code can not be blank."
        },
        label='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Zip Code', 'size': '11'})
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        super(BaseForm, self).__init__(*args, **kwargs)

    def get_success_url(self, instance):
        return reverse('workspace:tool_object_after_save_preview', kwargs={'workspace': instance.workspace.slug, 'tool': instance.workspace.tools.filter(slug=instance.tool_slug).first().slug, 'slug': instance.slug})

    def save(self):
        if self.instance is not None:
            # use the currently associated user
            user = self.instance.user
            is_new = False

        else:
            # Ensure we have a customer with this info
            customer_service = EnsureCustomerService(email=self.cleaned_data.get('signatory_email'),
                                                     full_name=self.cleaned_data.get('signatory_full_name'))
            customer_service.process()
            user = customer_service.user
            is_new = customer_service.is_new

        engageletter, is_new = user.engagementletter_set.get_or_create(workspace=self.workspace, user=user)
        engageletter.data.update(**self.cleaned_data)  # update the data
        engageletter.workspace = self.workspace
        engageletter.save()

        self.issue_signals(instance=engageletter)

        return engageletter


@parsleyfy
class LawyerForm(BaseForm):
    file_number = forms.CharField(
        error_messages={
            'required': "File number can not be blank."
        },
        help_text='',
        label='File number',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '000940001', 'size': '31'})
    )

    date_of_letter = forms.DateField(
        help_text='',
        input_formats=['%B %d, %Y', '%Y-%m-%d %H:%M:%S'],
        label='Date of letter',
        widget=forms.DateInput(
            attrs={
                'autocomplete': 'off',
                'data-toggle': 'datepicker'
            },
            format='%B %d, %Y'
        )
    )

    signatory_full_name = forms.CharField(
        error_messages={
            'required': "Signatory name can not be blank."
        },
        help_text='',
        label='Full name',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'John Smith', 'size': '40'})
    )

    signatory_email = forms.EmailField(
        error_messages={
            'invalid': "Signatory email is invalid.",
            'required': "Signatory email can not be blank."
        },
        help_text='',
        label='Email address',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'john@acmeinc.com', 'size': '40'})
    )

    signatory_title = forms.CharField(
        error_messages={
            'required': "Signatory title can not be blank."
        },
        label='Title',
        help_text='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'CEO', 'size': '20'})
    )

    rate_hourly_from = forms.DecimalField(
        decimal_places=2,
        label='',
        help_text='',
        max_digits=10,
        required=False,
        widget=forms.NumberInput(attrs={'style': 'width: 100px;'})
    )

    rate_hourly_to = forms.DecimalField(
        decimal_places=2,
        label='',
        help_text='',
        max_digits=10,
        required=False,
        widget=forms.NumberInput(attrs={'style': 'width: 100px;'})
    )

    rate_hourly_increments = forms.IntegerField(
        label='',
        help_text='',
        required=False,
        widget=forms.NumberInput(attrs={'style': 'width: 100px;'})
    )

    rate_flat_fee = forms.DecimalField(
        decimal_places=2,
        label='Flat-rate fee',
        help_text='',
        max_digits=10,
        required=False,
        widget=forms.NumberInput
    )

    legal_services = SummernoteField(
        error_messages={
            'required': "Legal services can not be blank."
        },
        help_text='',
        label='Legal services',
        required=True
    )

    service_description = SummernoteField(
        error_messages={
            'required': "Engagement description can not be blank."
        },
        help_text='',
        label='Description of engagement',
        required=True
    )

    fees = SummernoteField(
        error_messages={
            'required': "Fees can not be blank."
        },
        help_text='',
        label='Fees',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(LawyerForm, self).__init__(*args, **kwargs)

        # change the required state on some fields
        self.fields['address1'].required = False
        self.fields['address2'].required = False
        self.fields['city'].required = False
        self.fields['state'].required = False
        self.fields['post_code'].required = False

        # set the readonly fields
        self.fields['address1'].widget.attrs['readonly'] = 'readonly'
        self.fields['address2'].widget.attrs['readonly'] = 'readonly'
        self.fields['city'].widget.attrs['readonly'] = 'readonly'
        self.fields['state'].widget.attrs['disabled'] = 'disabled'
        self.fields['post_code'].widget.attrs['readonly'] = 'readonly'

        self.helper.layout = Layout(
            HTML('{% include "partials/form-errors.html" with form=form %}'),
            Div(
                HTML('<legend>Signatory details</legend>'),
                Div(
                    'signatory_full_name',
                    'signatory_email',
                    css_class='form-inline'
                ),
                AppendedText('signatory_title', 'at %s' % self.workspace.name),
            ),
            Div(
                HTML('<legend>Engagement Letter Information</legend>'),
                Div(
                    'file_number',
                    FieldWithButtons(
                        'date_of_letter',
                        StrictButton('<span class="fui-calendar"></span>'),
                        css_class='datetime'
                    ),
                    css_class='form-inline'
                ),
                'legal_services',
                'service_description',

                HTML('<label class="control-label">Hourly Rates</label>'),
                Div(
                    HTML('<span class="help-block">From</span>'),
                    PrependedText('rate_hourly_from', '$'),
                    HTML('<span class="help-block">to</span>'),
                    PrependedText('rate_hourly_to', '$'),
                    HTML('<span class="help-block">per hour</span>'),
                    HTML('<span class="help-block">, billed in increments of</span>'),
                    AppendedText('rate_hourly_increments', 'hour(s)'),
                    css_class='form-group form-inline'
                ),
                'rate_flat_fee',

                'fees',
            ),
            Div(
                HTML('<legend>Additional details (Client to complete)</legend>'),
                'address1',
                'address2',
                'city',
                Div(
                    'state',
                    'post_code',
                    css_class='form-inline'
                ),
                css_class='dialog dialog-info form-dialog'
            ),
            ButtonHolder(
                Submit('submit', 'Continue', css_class='btn btn-primary btn-lg btn-wide'),
                css_class='form-group'
            )
        )

    def issue_signals(self, instance):
        instance.markers.marker('lawyer_complete_form').issue_signals(request=self.request, instance=instance, actor=self.user)


@parsleyfy
class CustomerForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'address1',
            'address2',
            'city',
            Div(
                'state',
                'post_code',
                css_class='form-inline'
            ),
            ButtonHolder(
                Submit('submit', 'Continue', css_class='btn-hg btn-primary'),
                css_class='form-group'
            )
        )

    def issue_signals(self, instance):
        instance.markers.marker('customer_complete_form').issue_signals(request=self.request, instance=instance, actor=self.user)


@parsleyfy
class LawyerEngagementLetterTemplateForm(forms.Form):
    """
    Override the base letterhead and add out template letter HTML
    """
    body = SummernoteField(required=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', self.request.user)

        super(LawyerEngagementLetterTemplateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Div(
                'body',
                css_class='row'
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn btn-primary btn-lg')
            )
        )

    def get_success_url(self):
        return reverse('workspace:tool_object_overview', kwargs={'workspace': self.instance.workspace.slug, 'tool': self.instance.workspace.tools.filter(slug=self.instance.tool_slug).first().slug, 'slug': self.instance.slug})

    def issue_signals(self):
        self.instance.markers.marker('lawyer_review_letter_text').issue_signals(request=self.request, instance=self.instance, actor=self.user)

    def save(self):
        body = self.cleaned_data.get('body')
        #
        # Get or create the Attachment object
        #
        attachment_object, is_new = Attachment.objects.get_or_create(tool=self.instance)
        #
        # if its new or the body has changed
        #
        if is_new is True or attachment_object.body != body:
            attachment_object.body = body
            #
            # Convert the doc html to a docx file and save it
            #
            service = WordService()
            file_object = service.generate(html=attachment_object.body)
            attachment_object.attachment.save(file_object.name, file_object)

        self.issue_signals()


@parsleyfy
class SignEngagementLetterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        super(SignEngagementLetterForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                css_class='form-inline'
            ),
            ButtonHolder(
                Submit('submit', 'Continue', css_class='btn-hg btn-primary'),
                css_class='form-group'
            )
        )
