# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.bootstrap import FieldWithButtons, PrependedText, StrictButton
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import ButtonHolder, Div, Field, Fieldset, HTML, Submit

from localflavor.us.forms import USSocialSecurityNumberField, USZipCodeField
from localflavor.us.us_states import USPS_CHOICES

from parsley.decorators import parsleyfy

from usps.validators import USPSTrackingCodeField

from toolkit.apps.workspace.mixins import WorkspaceToolFormMixin
from toolkit.apps.workspace.services import EnsureCustomerService
from toolkit.apps.workspace.services import USPSTrackingService
from toolkit.core.fields import HTMLField
from toolkit.mixins import ModalForm

from .models import EightyThreeB
from .signals import customer_complete_form, lawyer_complete_form

import datetime

import logging
logger = logging.getLogger('django.request')


def _current_year():
    return datetime.datetime.utcnow().year


class BaseEightyThreeBForm(WorkspaceToolFormMixin):
    client_full_name = forms.CharField(
        error_messages={
            'required': "Taxpayer's name can not be blank."
        },
        help_text='',
        label='Full name',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Taxpayer\'s full name', 'size': '40'})
    )

    client_email = forms.EmailField(
        error_messages={
            'invalid': "Taxpayer's email is invalid.",
            'required': "Taxpayer's email can't be blank."
        },
        help_text='',
        label='Email address',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Taxpayer\'s email address', 'size': '40'})
    )

    company_name = forms.CharField(
        error_messages={
            'required': "Client name can't be blank."
        },
        help_text='',
        label='Company name',
        widget=forms.TextInput(attrs={'placeholder': 'Company name', 'size': '40'})
    )

    address1 = forms.CharField(
        error_messages={
            'required': "Address can't be blank."
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
            'required': "City can't be blank."
        },
        label='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'City', 'size': '40'})
    )

    state = forms.ChoiceField(
        choices=USPS_CHOICES,
        error_messages={
            'required': "State can't be blank."
        },
        label='',
        help_text='',
        initial='CA',
        required=True
    )

    post_code = USZipCodeField(
        error_messages={
            'required': "Zip code can't be blank."
        },
        label='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Zip Code', 'size': '11'})
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
        help_text='A copy of your 83(b) election needs to be included with your tax return for the year in which the property is received (note that this often precludes electronic filing). If you provide us with an email address for your accountant, we will email a copy of your 83(b) election to them for inclusion in your tax returns. You should always follow up with your accountant.',
        label='Your accountant\'s email address',
        required=False,
        widget=forms.EmailInput(attrs={'size': '40'})
    )

    has_spouse = forms.BooleanField(
        help_text='',
        label='Yes, I have a spouse',
        required=False,
    )

    date_of_property_transfer = forms.DateField(
        error_messages={
            'invalid': "Property transfer date is invalid.",
            'required': "Property transfer date can't be blank."
        },
        help_text='The filing deadline is 30 days from this date. Your election must be post-marked no later than <span id="filing-deadline"></span>.',
        input_formats=['%B %d, %Y', '%Y-%m-%d %H:%M:%S'],
        label='Date on which the property was transferred',
        widget=forms.DateInput(
            attrs={
                'autocomplete': 'off',
                'data-toggle': 'datepicker'
            },
            format='%B %d, %Y'
        )
    )

    description = HTMLField(
        error_messages={
            'required': "Property description can't be blank."
        },
        label='Description of property with respect to which election is being made',
        initial='{{ total_shares_purchased }} shares (the “Shares”) of the Common Stock of {{ company_name }}, Inc. (the “Company”) (${{ price_paid_per_share }} per share)'
    )

    tax_year = forms.IntegerField(
        error_messages={
            'required': "Tax year can't be blank."
        },
        label='Taxable year for which the election is being made',
        initial=_current_year,
        widget=forms.NumberInput(attrs={'size': '4'})
    )

    nature_of_restrictions = HTMLField(
        error_messages={
            'required': "Nature of restrictions can't be blank."
        },
        label='Nature of restrictions to which property is subject',
        initial="The Shares may be repurchased by the Company, or its assignee, upon the occurrence of certain events. This right lapses with regard to a portion of the Shares over time."
    )

    transfer_value_share = forms.DecimalField(
        error_messages={
            'required': "Transfer value per share can't be blank."
        },
        help_text='paid per share',
        label='Value per share at time of transfer',
        initial='0.0001',
        widget=forms.TextInput(attrs={'size': '10'})
    )

    total_shares_purchased = forms.DecimalField(
        error_messages={
            'required': "Total shares purchased can't be blank."
        },
        help_text='',
        label='Total number of shares purchased',
        initial='100',
        widget=forms.NumberInput(attrs={'size': '10'})
    )

    price_paid_per_share = forms.DecimalField(
        error_messages={
            'required': "Price paid per share can't be blank."
        },
        help_text='paid per share',
        label='Actual price paid per share',
        initial='0.0001',
        widget=forms.TextInput(attrs={'size': '10'})
    )

    def __init__(self, *args, **kwargs):
        super(BaseEightyThreeBForm, self).__init__(*args, **kwargs)

        if self.fields['company_name'].initial in ['', None]:
            self.fields['company_name'].initial = self.workspace.name

    def get_success_url(self, instance):
        return reverse('workspace:tool_object_after_save_preview', kwargs={'workspace': instance.workspace.slug, 'tool': instance.workspace.tools.filter(slug=instance.tool_slug).first().slug, 'slug': instance.slug})

    def save(self):
        if self.instance is not None:
            # use the currently associated user
            user = self.instance.user
            is_new = False

        else:
            # Ensure we have a customer with this info
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


@parsleyfy
class CustomerEightyThreeBForm(BaseEightyThreeBForm):
    disclaimer_agreed = forms.BooleanField(
        error_messages={
            'required': "You must agree with the disclaimer."
        },
        help_text='',
        label='I agree',
        required=True,
    )

    details_confirmed = forms.BooleanField(
        error_messages={
            'required': "You must confirm that the details are correct."
        },
        help_text='',
        label='I confirm that the details above are correct',
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(CustomerEightyThreeBForm, self).__init__(*args, **kwargs)

        # set up the hidden fields that still need to be submitted
        self.fields['client_full_name'].widget = forms.HiddenInput()
        self.fields['client_email'].widget = forms.HiddenInput()
        self.fields['company_name'].widget = forms.HiddenInput()
        self.fields['date_of_property_transfer'].widget = forms.HiddenInput()
        self.fields['description'].widget = forms.HiddenInput()
        self.fields['tax_year'].widget = forms.HiddenInput()
        self.fields['nature_of_restrictions'].widget = forms.HiddenInput()
        self.fields['total_shares_purchased'].widget = forms.HiddenInput()
        self.fields['price_paid_per_share'].widget = forms.HiddenInput()
        self.fields['transfer_value_share'].widget = forms.HiddenInput()

        self.helper.layout = Layout(
            HTML('{% include "partials/form-errors.html" with form=form %}'),
            Div(
                HTML('<h4>Disclaimer</h4>'),
                HTML('<p>LawPal Inc. is not an attorney or law firm and this is not intended as legal advice. \
                      Neither is LawPal, Inc. a tax advisor and this is not intended as tax advice. \
                      You should consult your own attorney and your own tax advisor on whether it is best to make the 83(b) election or not. \
                      LawPal, Inc. can only provide self help services at your specific direction.</p>'),
                HTML('<p><strong>THE FILING OF THIS 83(B) ELECTION IS YOUR RESPONSIBILITY. \
                      YOU MUST FILE THIS FORM WITHIN 30 DAYS OF PURCHASING THE SHARES.</strong></p>'),
                Field('disclaimer_agreed', template='public/bootstrap3/t_and_c.html'),
                css_class='alert'
            ),
            Div(
                # Your details
                'client_full_name',
                'client_email',
                'company_name',
            ),
            Div(
                HTML('<legend>Address</legend>'),
                'address1',
                'address2',
                'city',
                Div(
                    'state',
                    'post_code',
                    css_class='form-inline'
                ),
                css_class='form-section'
            ),
            Div(
                HTML('<legend>Additional details</legend>'),

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
                HTML('<label>Do you have a spouse?</label>'),
                Field('has_spouse', template='public/bootstrap3/t_and_c.html'),
                css_class='form-section'
            ),
            Div(
                HTML('<legend>Please confirm the following is correct</legend>'),
                HTML('<p><small>For your convenience the Company\'s attorney has entered the following information. If you have any questions, please check with them directly.</small></p> <br />'),


                HTML('<p>{{ form.date_of_property_transfer.label }}</p>'),
                HTML('<blockquote><p>{{ form.date_of_property_transfer.value|date:"F jS, Y" }}</p></blockquote>'),
                'date_of_property_transfer',

                HTML('<p>{{ form.description.label }}</p>'),
                HTML('<blockquote><p>{{ form.description.value|safe }}</p></blockquote>'),
                'description',

                HTML('<p>{{ form.tax_year.label }}</p>'),
                HTML('<blockquote><p>{{ form.tax_year.value }}</p></blockquote>'),
                'tax_year',

                HTML('<p>{{ form.nature_of_restrictions.label }}</p>'),
                HTML('<blockquote><p>{{ form.nature_of_restrictions.value|safe }}</p></blockquote>'),
                'nature_of_restrictions',

                Field('details_confirmed', template='public/bootstrap3/t_and_c.html'),
                css_class='dialog dialog-info form-section form-dialog'
            ),


            'total_shares_purchased',  # hidden widget
            'price_paid_per_share',  # hidden widget
            'transfer_value_share',  # hidden widget

            ButtonHolder(
                Submit('submit', 'Continue', css_class='btn-hg btn-primary'),
                css_class='form-group'
            )
        )

    def clean(self):
        """
        If the ssn or itin is not specified and we have a blank value
        """
        # we use data instead of cleaned_data to prevent multiple error messages
        # we're only testing for the presence of 2 values, not their validity
        ssn = self.data.get('ssn', None)
        itin = self.data.get('itin', None)

        if ssn in ['', None] and itin in ['', None]:
            raise forms.ValidationError("Please specify either an SSN or an ITIN.")

        return self.cleaned_data

    def issue_signals(self, instance):
        customer_complete_form.send(sender=self.request, instance=instance, actor=self.user)


@parsleyfy
class LawyerEightyThreeBForm(BaseEightyThreeBForm):
    def __init__(self, *args, **kwargs):
        super(LawyerEightyThreeBForm, self).__init__(*args, **kwargs)

        # change the required state on some fields
        self.fields['address1'].required = False
        self.fields['city'].required = False
        self.fields['state'].required = False
        self.fields['post_code'].required = False

        # set the readonly fields
        self.fields['address1'].widget.attrs['readonly'] = 'readonly'
        self.fields['address2'].widget.attrs['readonly'] = 'readonly'
        self.fields['city'].widget.attrs['readonly'] = 'readonly'
        self.fields['state'].widget.attrs['disabled'] = 'disabled'
        self.fields['post_code'].widget.attrs['readonly'] = 'readonly'
        self.fields['ssn'].widget.attrs['readonly'] = 'readonly'
        self.fields['itin'].widget.attrs['readonly'] = 'readonly'
        self.fields['accountant_email'].widget.attrs['readonly'] = 'readonly'
        self.fields['has_spouse'].widget.attrs['disabled'] = 'disabled'

        self.helper.layout = Layout(
            HTML('{% include "partials/form-errors.html" with form=form %}'),
            Div(
                HTML('<legend>Taxpayer Details</legend>'),
                Div(
                    'client_full_name',
                    'client_email',
                    css_class='form-inline'
                ),
                Div(
                    'company_name',
                ),
            ),
            Div(
                HTML('<legend>83(b) Election Information</legend>'),
                FieldWithButtons(
                    'date_of_property_transfer',
                    StrictButton('<span class="fui-calendar"></span>'),
                    css_class='datetime'
                ),
                'total_shares_purchased',
                PrependedText('transfer_value_share', '$'),
                PrependedText('price_paid_per_share', '$', css_class='form-inline'),
                'description',
                'tax_year',
                'nature_of_restrictions',
            ),
            ButtonHolder(
                Submit('submit', 'Continue', css_class='btn-hg btn-primary'),
                css_class='form-group'
            )
        )

    def clean_date_of_property_transfer(self):
        date = self.cleaned_data.get('date_of_property_transfer')

        if date < (datetime.date.today() - datetime.timedelta(days=25)):
            raise forms.ValidationError('LawPal requires a minimum of 5 days to complete the election. The date of property transfer was greater than than 25 days ago.')

        return date

    def issue_signals(self, instance):
        lawyer_complete_form.send(sender=self.request, instance=instance, actor=self.user)


@parsleyfy
class TrackingCodeForm(ModalForm, forms.ModelForm):
    title = 'Your 83b Postage Tracking Code'

    tracking_code = USPSTrackingCodeField(
        error_messages={
            'required': "Tracking code can't be blank."
        },
        help_text='Please provide the Registered Post Tracking Code (USPS)',
        widget=forms.TextInput(attrs={'placeholder': 'Tracking code', 'size': '40'})
    )
    user = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        fields = ['user']
        model = EightyThreeB

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = reverse('eightythreeb:tracking_code', kwargs={'slug': kwargs['instance'].slug})

        self.helper.layout = Layout(
            'tracking_code',
        )

        super(TrackingCodeForm, self).__init__(*args, **kwargs)

        self.fields['tracking_code'].initial = self.instance.tracking_code

    def clean_tracking_code(self):
        tracking_code = self.cleaned_data.get('tracking_code')

        self.instance.markers.marker('valid_usps_tracking_marker').issue_signals(request=self,
                                                                                 instance=self.instance,
                                                                                 actor=self.instance.user,
                                                                                 tracking_code=tracking_code)

        service = USPSTrackingService()

        try:
            usps_response = service.track(tracking_code=tracking_code)
            service.record(instance=self.instance, usps_response=usps_response)
        except Exception as e:
            logger.error('Invalid Tracking Code %s' % (tracking_code,))
            #raise forms.ValidationError('The Tracking code is not valid: %s' % e)

        return tracking_code

    def clean_user(self):
        # dont allow override from form
        return self.instance.user

    def save(self, **kwargs):
        # save to data
        self.instance.tracking_code = self.cleaned_data.get('tracking_code')
        return super(TrackingCodeForm, self).save(**kwargs)


@parsleyfy
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = EightyThreeB

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {
            'parsley-validate': '',
        }

        self.helper.layout = Layout(
            ButtonHolder(
                Submit('submit', 'Upload', css_class='btn-hg btn-primary'),
                css_class='form-group'
            )
        )

        super(AttachmentForm, self).__init__(*args, **kwargs)
