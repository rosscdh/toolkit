# -*- coding: utf-8 -*-
from django.template import Context
from django.template.loader import get_template
from django.template.loaders.app_directories import Loader
from django.template import Template
from django.utils.safestring import mark_safe

from datetime import date, datetime, timedelta

from toolkit.apps.workspace.services import USPSResponse


class HTMLMixin(object):
    """
    Mixin to deal with loading the model templates
    and template
    """
    @property
    def template(self):
        return get_template(self.pdf_template_name)

    def template_source(self, template_name):
        source_loader = Loader()
        source, file_path = source_loader.load_template_source(template_name)
        return source

    def get_context_data(self, **kwargs):
        context_data = self.data.copy()  # must copy to avoid reference update

        context_data.update({'object': self})
        # update with kwargs passed in which take priority for overrides
        context_data.update(kwargs)
        local_context = Context(context_data)
        # Mark strings as safe
        for k, v in context_data.items():
            if type(v) in [str, unicode]:
                t = Template(mark_safe(v))
                context_data[k] = t.render(local_context)

        return context_data

    def html(self, **kwargs):
        context_data = self.get_context_data(**kwargs)

        context = Context(context_data)
        source = self.template.render(context)
        return source


class TransferAndFilingDatesMixin(object):
    @property
    def days_left(self):
        return (self.filing_date - date.today()).days

    def get_filing_date(self):
        return self.transfer_date + timedelta(days=30)

    def get_transfer_date(self):
        transfer_date = self.data.get('date_of_property_transfer', None)
        transfer_date_type = type(transfer_date)

        if transfer_date_type in [str]:
            return datetime.strptime(transfer_date, '%Y-%m-%d').date()

        if transfer_date_type in [date]:
            return transfer_date
        return None


class StatusMixin(object):
    @property
    def current_status(self):
        return self.STATUS.get_desc_by_value(self.status)

    @property
    def display_status(self):
        """ alias for current_status """
        return self.current_status

    def markers_complete(self):
        return self.data.get('markers')


class USPSReponseMixin(object):
    @property
    def tracking_code(self):
        return self.data.get('tracking_code')

    @tracking_code.setter
    def tracking_code(self, value):
        self.data['tracking_code'] = value

    @property
    def usps(self):
        return self.data.get('usps', {})

    @property
    def usps_current_status(self):
        return self.usps.get('current_status', None)

    @property
    def usps_current_summary(self):
        return self.usps.get('current_summary', None)

    @property
    def usps_waypoints(self):
        return self.usps.get('waypoints', [])

    @property
    def usps_log(self):
        """
        Return a list of stored usps_logs as responses
        """
        return [USPSResponse(usps_response=r, tracking_code=self.tracking_code) for r in self.data.get('usps_log', [])]


class IRSMixin(object):
    """
    Provide helper methods to allow access to relevant irs addresses and details
    based on a ruleset
    """
    SPOUSAL_SIGNATURE_STATES = (
        'AZ',  # Arizona
        'CA',  # California
        'ID',  # Idaho
        'LA',  # Louisiana
        'NV',  # Nevada
        'NM',  # New Mexico
        'TX',  # Texas
        'WA',  # Washington
        'WI',  # Wisconsin
    )

    STATE_ADDRESSES = (
        (
            (
                # Florida, Louisiana, Mississippi, Texas
                'FL', 'LA', 'MS', 'TX'
            ),
            {
                # Default
                'address1': 'Department of the Treasury',
                'address2': 'Internal Revenue Service',
                'city': 'Austin',
                'state': 'TX',
                'zip': '73301-0002'
            },
            {
                # Payment
                'address1': 'Internal Revenue Service',
                'address2': 'P.O. Box 1214',
                'city': 'Charlotte',
                'state': 'NC',
                'zip': '28201-1214'
            }
        ),
        (
            (
                # Alaska, Arizona, California, Colorado,
                # Hawaii, Idaho, Nevada, New Mexico,
                # Oregon, Utah, Washington, Wyoming
                'AK', 'AZ', 'CA', 'CO',
                'HI', 'ID', 'NV', 'NM',
                'OR', 'UT', 'WA', 'WY'
            ),
            {
                # Default
                'address1': 'Department of the Treasury',
                'address2': 'Internal Revenue Service',
                'city': 'Fresno',
                'state': 'CA',
                'zip': '93888-0002'
            },
            {
                # Payment
                'address1': 'Internal Revenue Service',
                'address2': 'P.O. Box 7704',
                'city': 'San Francisco',
                'state': 'CA',
                'zip': '94120-7704'
            }
        ),
        (
            (
                # Arkansas, Illinois, Indiana, Iowa, Kansas,
                # Michigan, Minnesota, Montana, Nebraska, North Dakota,
                # Ohio, Oklahoma, South Dakota, Wisconsin
                'AR', 'IL', 'IN', 'IA', 'KS',
                'MI', 'MN', 'MT', 'NE', 'ND',
                'OH', 'OK', 'SD', 'WI'
            ),
            {
                # Default
                'address1': 'Department of the Treasury',
                'address2': 'Internal Revenue Service',
                'city': 'Fresno',
                'state': 'CA',
                'zip': '93888-0002'
            },
            {
                # Payment
                'address1': 'Internal Revenue Service',
                'address2': 'P.O. Box 802501',
                'city': 'Cincinnati',
                'state': 'OH',
                'zip': '45280-2501'
            }
        ),
        (
            (
                # Alabama, Georgia, Kentucky,
                # Missouri, New Jersey, North Carolina
                # South Carolina, Tennessee, Virginia
                'AL', 'GA', 'KY',
                'MO', 'NJ', 'NC',
                'SC', 'TN', 'VA'
            ),
            {
                # Default
                'address1': 'Department of the Treasury',
                'address2': 'Internal Revenue Service',
                'city': 'Kansas City',
                'state': 'MO',
                'zip': '64999-0002'
            },
            {
                # Payment
                'address1': 'Internal Revenue Service',
                'address2': 'P.O. Box 931000',
                'city': 'Louisville',
                'state': 'KY',
                'zip': '40293-1000'
            }
        ),
        (
            (
                # Connecticut, Delaware, District of Columbia, Maine
                # Maryland, Massachusetts, New Hampshire, New York
                # Pennsylvania, Rhode Island, Vermont, West Virginia
                'CT', 'DE', 'DC', 'ME',
                'MD', 'MA', 'NH', 'NY',
                'PA', 'RI', 'VT', 'WV'
            ),
            {
                # Default
                'address1': 'Department of the Treasury',
                'address2': 'Internal Revenue Service',
                'city': 'Kansas City',
                'state': 'MO',
                'zip': '64999-0002'
            },
            {
                # Payment
                'address1': 'Internal Revenue Service',
                'address2': 'P.O. Box 37008',
                'city': 'Hartford',
                'state': 'CT',
                'zip': '06176-0008'
            }
        ),
        (
            (
                # American Samoa, Guam, Northern Mariana Islands,
                # Puerto Rico, Virgin Islands
                'AS', 'GU', 'MP', 'PR', 'VI'
            ),
            {
                # Default
                'address1': 'Department of the Treasury',
                'address2': 'Internal Revenue Service',
                'city': 'Austin',
                'state': 'TX',
                'zip': '73301-0215',
                'country': 'USA'
            },
            {
                # Payment
                'address1': 'Internal Revenue Service',
                'address2': 'P.O. Box 1303',
                'city': 'Charlotte',
                'state': 'NC',
                'zip': '28201-1303',
                'country': 'USA'
            }
        )
    )

    def get_irs_address(self, state):
        for states, address, payment_address in self.STATE_ADDRESSES:
            if state in states:
                return address

        return self.STATE_ADDRESSES[-1][1]

    def get_irs_payment_address(self, state):
        for states, address, payment_address in self.STATE_ADDRESSES:
            if state in states:
                return payment_address

        return self.STATE_ADDRESSES[-1][2]

    @property
    def irs_address(self):
        return self.get_irs_address(self.customer_state)

    @property
    def irs_payment_address(self):
        return self.get_irs_payment_address(self.customer_state)

    @property
    def customer_state(self):
        return self.data.get('state', None)

    @property
    def customer_has_spouse(self):
        return 'has_spouse' in self.data and self.data['has_spouse'] is True

    @property
    def customer_in_spousal_state(self):
        return self.customer_state in self.SPOUSAL_SIGNATURE_STATES

    @property
    def spouse_must_sign(self):
        return self.customer_has_spouse is True and self.customer_in_spousal_state is True
