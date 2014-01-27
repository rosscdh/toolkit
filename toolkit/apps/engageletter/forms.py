# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import ButtonHolder, Div, HTML, Submit

from parsley.decorators import parsleyfy

from localflavor.us.us_states import USPS_CHOICES
from localflavor.us.forms import USZipCodeField

from toolkit.apps.workspace.mixins import WorkspaceToolFormMixin
from toolkit.apps.workspace.services import EnsureCustomerService

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
    date_of_property_transfer = forms.DateField(
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
        label='Signatory title',
        help_text='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'CEO', 'size': '40'})
    )

    company_name = forms.CharField(
        error_messages={
            'required': "Company name can not be blank."
        },
        label='Company name',
        help_text='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Acme Inc', 'size': '40'})
    )

    # file_number = forms.CharField()
    # rate_hourly_from = forms.DecimalField(max_digits=10, decimal_places=2)
    # rate_hourly_to = forms.DecimalField(max_digits=10, decimal_places=2)
    # rate_hourly_increments = forms.IntegerField()
    # rate_flat_fee = forms.DecimalField(max_digits=10, decimal_places=2)

    legal_services = forms.CharField(
        error_messages={
            'required': "Legal services can not be blank."
        },
        help_text='',
        label='Legal services',
        required=True,
        widget=forms.Textarea(attrs={
            'cols': '80',
            'data-toggle': 'summernote'
        })
    )

    service_description = forms.CharField(
        error_messages={
            'required': "Engagement description can not be blank."
        },
        help_text='',
        label='Description of engagement',
        required=True,
        widget=forms.Textarea(attrs={
            'cols': '80',
            'data-toggle': 'summernote'
        })
    )

    fees = forms.CharField(
        error_messages={
            'required': "Fees can not be blank."
        },
        help_text='',
        label='Fees',
        required=True,
        widget=forms.Textarea(attrs={
            'cols': '80',
            'data-toggle': 'summernote'
        })
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
                Div(
                    'signatory_title',
                    'company_name',
                    css_class='form-inline'
                ),
            ),
            Div(
                HTML('<legend>Engagement Letter Information</legend>'),
                FieldWithButtons(
                    'date_of_property_transfer',
                    StrictButton('<span class="fui-calendar"></span>'),
                    css_class='datetime'
                ),
                'legal_services',
                'service_description',
                'fees',

                # 'file_number',
                # 'rate_hourly_from',
                # 'rate_hourly_to',
                # 'rate_hourly_increments',
                # 'rate_flat_fee',
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

    def get_success_url(self, instance):
        return reverse('workspace:tool_object_after_save_preview', kwargs={'workspace': instance.workspace.slug, 'tool': instance.workspace.tools.filter(slug=instance.tool_slug).first().slug, 'slug': instance.slug})

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
    body = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': '100'}))

    def __init__(self, instance, user, *args, **kwargs):
        self.instance = instance
        self.user = user

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
    def save(self):
        # @TODO make this save the template
        pass


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
