# -*- coding: utf-8 -*-
from django.template import loader
from django.utils.safestring import mark_safe

from datetime import date, datetime, timedelta

from toolkit.apps.workspace.services import USPSResponse


class IsDeletedMixin(object):
    def delete(self, *args, **kwargs):
        """
        override delete and set is_deleted = True if we have that attrib
        """
        if hasattr(self, 'is_deleted'):
            self.is_deleted = True
            self.save(update_fields=['is_deleted'])
        else:
            super(IsDeletedMixin, self).delete(*args, **kwargs)


class HTMLMixin(object):
    @property
    def template(self):
        return loader.get_template(self.template_name)

    def html(self, **kwargs):
        context_data = self.data.copy() # must copy to avoid reference update

        # Mark strings as safe
        for k, v in context_data.items():
            if type(v) in [str, unicode]:
                context_data[k] = mark_safe(v)

        context_data.update({'object': self})

        # update with kwargs passed in which take priority for overrides
        context_data.update(kwargs)

        context = loader.Context(context_data)
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
        return self.STATUS_83b.get_desc_by_value(self.status)

    def current_markers(self):
        return self.data.get('markers')

    def next_status_step(self):
        return None

    def prev_status_step(self):
        return None


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
    spousal_signature_states = (
        'AZ', # Arizona
        'CA', # California
        'ID', # Idaho
        'LA', # Louisiana
        'NV', # Nevada
        'NM', # New Mexico
        'TX', # Texas
        'WA', # Washington
        'WI', # Wisconsin
    )
    irs_state_address_paymentaddress = (
        (('FL', 'LA', 'MS', 'TX'),
        'Department of the Treasury<br/>Internal Revenue Service<br/>Austin, TX 73301-0002',  # Default
        'Internal Revenue Service<br/>P.O. Box 1214<br/>Charlotte, NC 28201-1214'),  # with Payment Cheque

        (('AK', 'AZ', 'CA', 'CO',
          'HI', 'ID', 'NV', 'NM',
          'OR', 'UT', 'WA', 'WY'),
        'Department of the Treasury<br/>Internal Revenue Service<br/>Fresno, CA 93888-0002',  # Default
        'Internal Revenue Service<br/>P.O. Box 7704<br/>San Francisco, CA 94120-7704'),  # with Payment Cheque

        (('AR', 'IL', 'IN', 'IA',
          'KS', 'MI', 'MN', 'MT',
          'NE', 'ND', 'OH', 'OK',
          'SD', 'ND', 'WI'),
        'Department of the Treasury<br/>Internal Revenue Service<br/>Fresno, CA 93888-0002',  # Default
        'Internal Revenue Service<br/>P.O. Box 802501<br/>Cincinnati, OH 45280-2501'),  # with Payment Cheque

        (('AL', 'GA', 'KY', 'MO',
          'NJ', 'NC', 'SC', 'TN',
          'VA'),
        'Department of the Treasury<br/>Internal Revenue Service<br/>Kansas City, MO 64999-0002',  # Default
        'Internal Revenue Service<br/>P.O. Box 931000<br/>Louisville, KY 40293-1000'),  # with Payment Cheque

        (('CT', 'DE', 'DC', 'ME',
          'MD', 'MA', 'NH', 'NY',
          'PA', 'RI', 'VT', 'WV'),
        'Department of the Treasury<br/>Internal Revenue Service<br/>Kansas City, MO 64999-0002',  # Default
        'Internal Revenue Service<br/>P.O. Box 37008<br/>Hartford, CT 06176-0008'),  # with Payment Cheque

        # as per http://uk.practicallaw.com/3-518-4832 && http://www.irs.gov/pub/irs-pdf/p570.pdf
        (('AS', 'PR', 'VI', 'ME',
          'MP'),
        'Department of the Treasury<br/>Internal Revenue Service<br/>Austin, TX 73301-0215<br/>USA',  # Default
        'Internal Revenue Service<br/>P.O. Box 1303<br/>Charlotte, NC 28201-1303<br/>USA'),  # with Payment Cheque
    )

    @property
    def customer_has_spouse(self):
        return 'has_spouse' in self.data and self.data['has_spouse'] is True

    @property
    def customer_state(self):
        return self.data.get('state', None)

    @property
    def customer_in_sposal_state(self):
        return self.customer_state in self.spousal_signature_states

    @property
    def spouse_must_sign(self):
        return self.customer_has_spouse is True and self.customer_in_sposal_state is True

    @property
    def irs_address(self):
        state = self.customer_state
        if state in ['', None]:
            return None

        else:
            for states, address, cheque_address in self.irs_state_address_paymentaddress:
                if state in states:
                    return mark_safe(address)
            # return the last default address
            return mark_safe(self.irs_state_address_paymentaddress[:-1][0][1])
