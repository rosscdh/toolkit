from django.test import TestCase

from toolkit.casper import BaseScenarios


class IRSAddressTest(BaseScenarios, TestCase):
    def setUp(self):
        super(IRSAddressTest, self).setUp()
        self.basic_workspace()

    def test_austin_texas_irs_address(self):
        states = (
            ('FL', 'Florida'),
            ('LA', 'Louisiana'),
            ('MS', 'Mississippi'),
            ('TX', 'Texas'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_address
            self.assertEquals(address.get('address1', None), 'Department of the Treasury')
            self.assertEquals(address.get('address2', None), 'Internal Revenue Service')
            self.assertEquals(address.get('city', None), 'Austin')
            self.assertEquals(address.get('state', None), 'TX')
            self.assertEquals(address.get('zip', None), '73301-0002')

    def test_fresno_california_irs_address(self):
        states = (
            ('AK', 'Alaska'),
            ('AZ', 'Arizona'),
            ('AR', 'Arkansas'),
            ('CA', 'California'),
            ('CO', 'Colorado'),
            ('HI', 'Hawaii'),
            ('ID', 'Idaho'),
            ('IL', 'Illinois'),
            ('IN', 'Indiana'),
            ('IA', 'Iowa'),
            ('KS', 'Kansas'),
            ('MI', 'Michigan'),
            ('MN', 'Minnesota'),
            ('MT', 'Montana'),
            ('NE', 'Nebraska'),
            ('NV', 'Nevada'),
            ('NM', 'New Mexico'),
            ('ND', 'North Dakota'),
            ('OH', 'Ohio'),
            ('OK', 'Oklahoma'),
            ('OR', 'Oregon'),
            ('SD', 'South Dakota'),
            ('UT', 'Utah'),
            ('WA', 'Washington'),
            ('WI', 'Wisconsin'),
            ('WY', 'Wyoming'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_address
            self.assertEquals(address.get('address1', None), 'Department of the Treasury')
            self.assertEquals(address.get('address2', None), 'Internal Revenue Service')
            self.assertEquals(address.get('city', None), 'Fresno')
            self.assertEquals(address.get('state', None), 'CA')
            self.assertEquals(address.get('zip', None), '93888-0002')

    def test_kansas_missouri_irs_address(self):
        states = (
            ('AL', 'Alabama'),
            ('CT', 'Connecticut'),
            ('DE', 'Delaware'),
            ('DC', 'District of Columbia'),
            ('GA', 'Georgia'),
            ('KY', 'Kentucky'),
            ('ME', 'Maine'),
            ('MD', 'Maryland'),
            ('MA', 'Massachusetts'),
            ('MO', 'Missouri'),
            ('NH', 'New Hampshire'),
            ('NJ', 'New Jersey'),
            ('NY', 'New York'),
            ('NC', 'North Carolina'),
            ('PA', 'Pennsylvania'),
            ('RI', 'Rhode Island'),
            ('SC', 'South Carolina'),
            ('TN', 'Tennessee'),
            ('VT', 'Vermont'),
            ('VA', 'Virginia'),
            ('WV', 'West Virginia'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_address
            self.assertEquals(address.get('address1', None), 'Department of the Treasury')
            self.assertEquals(address.get('address2', None), 'Internal Revenue Service')
            self.assertEquals(address.get('city', None), 'Kansas City')
            self.assertEquals(address.get('state', None), 'MO')
            self.assertEquals(address.get('zip', None), '64999-0002')

    def test_us_territory_irs_address(self):
        states = (
            ('AS', 'American Samoa'),
            ('GU', 'Guam'),
            ('MP', 'Northern Mariana Islands'),
            ('PR', 'Puerto Rico'),
            ('VI', 'Virgin Islands'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_address
            self.assertEquals(address.get('address1', None), 'Department of the Treasury')
            self.assertEquals(address.get('address2', None), 'Internal Revenue Service')
            self.assertEquals(address.get('city', None), 'Austin')
            self.assertEquals(address.get('state', None), 'TX')
            self.assertEquals(address.get('zip', None), '73301-0215')
            self.assertEquals(address.get('country', None), 'USA')

    def test_international_irs_address(self):
        del(self.eightythreeb.data['state'])

        address = self.eightythreeb.irs_address
        self.assertEquals(address.get('address1', None), 'Department of the Treasury')
        self.assertEquals(address.get('address2', None), 'Internal Revenue Service')
        self.assertEquals(address.get('city', None), 'Austin')
        self.assertEquals(address.get('state', None), 'TX')
        self.assertEquals(address.get('zip', None), '73301-0215')
        self.assertEquals(address.get('country', None), 'USA')


class IRSPaymentAddressTest(BaseScenarios, TestCase):
    def setUp(self):
        super(IRSPaymentAddressTest, self).setUp()
        self.basic_workspace()

    def test_charlotte_north_carolina_irs_payment_address(self):
        states = (
            ('FL', 'Florida'),
            ('LA', 'Louisiana'),
            ('MS', 'Mississippi'),
            ('TX', 'Texas'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_payment_address
            self.assertEquals(address.get('address1', None), 'Internal Revenue Service')
            self.assertEquals(address.get('address2', None), 'P.O. Box 1214')
            self.assertEquals(address.get('city', None), 'Charlotte')
            self.assertEquals(address.get('state', None), 'NC')
            self.assertEquals(address.get('zip', None), '28201-1214')

    def test_cincinnati_ohio_irs_payment_address(self):
        states = (
            ('AR', 'Arkansas'),
            ('IL', 'Illinois'),
            ('IN', 'Indiana'),
            ('IA', 'Iowa'),
            ('KS', 'Kansas'),
            ('MI', 'Michigan'),
            ('MN', 'Minnesota'),
            ('MT', 'Montana'),
            ('NE', 'Nebraska'),
            ('ND', 'North Dakota'),
            ('OH', 'Ohio'),
            ('OK', 'Oklahoma'),
            ('SD', 'South Dakota'),
            ('WI', 'Wisconsin'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_payment_address
            self.assertEquals(address.get('address1', None), 'Internal Revenue Service')
            self.assertEquals(address.get('address2', None), 'P.O. Box 802501')
            self.assertEquals(address.get('city', None), 'Cincinnati')
            self.assertEquals(address.get('state', None), 'OH')
            self.assertEquals(address.get('zip', None), '45280-2501')

    def test_hartford_connecticut_irs_payment_address(self):
        states = (
            ('CT', 'Connecticut'),
            ('DE', 'Delaware'),
            ('DC', 'District of Columbia'),
            ('ME', 'Maine'),
            ('MD', 'Maryland'),
            ('MA', 'Massachusetts'),
            ('NH', 'New Hampshire'),
            ('NY', 'New York'),
            ('PA', 'Pennsylvania'),
            ('RI', 'Rhode Island'),
            ('VT', 'Vermont'),
            ('WV', 'West Virginia'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_payment_address
            self.assertEquals(address.get('address1', None), 'Internal Revenue Service')
            self.assertEquals(address.get('address2', None), 'P.O. Box 37008')
            self.assertEquals(address.get('city', None), 'Hartford')
            self.assertEquals(address.get('state', None), 'CT')
            self.assertEquals(address.get('zip', None), '06176-0008')

    def test_louisville_kentucky_irs_payment_address(self):
        states = (
            ('AL', 'Alabama'),
            ('GA', 'Georgia'),
            ('KY', 'Kentucky'),
            ('MO', 'Missouri'),
            ('NJ', 'New Jersey'),
            ('NC', 'North Carolina'),
            ('SC', 'South Carolina'),
            ('TN', 'Tennessee'),
            ('VA', 'Virginia'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_payment_address
            self.assertEquals(address.get('address1', None), 'Internal Revenue Service')
            self.assertEquals(address.get('address2', None), 'P.O. Box 931000')
            self.assertEquals(address.get('city', None), 'Louisville')
            self.assertEquals(address.get('state', None), 'KY')
            self.assertEquals(address.get('zip', None), '40293-1000')

    def test_san_francisco_california_irs_payment_address(self):
        states = (
            ('AK', 'Alaska'),
            ('AZ', 'Arizona'),
            ('CA', 'California'),
            ('CO', 'Colorado'),
            ('HI', 'Hawaii'),
            ('ID', 'Idaho'),
            ('NV', 'Nevada'),
            ('NM', 'New Mexico'),
            ('OR', 'Oregon'),
            ('UT', 'Utah'),
            ('WA', 'Washington'),
            ('WY', 'Wyoming')
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_payment_address
            self.assertEquals(address.get('address1', None), 'Internal Revenue Service')
            self.assertEquals(address.get('address2', None), 'P.O. Box 7704')
            self.assertEquals(address.get('city', None), 'San Francisco')
            self.assertEquals(address.get('state', None), 'CA')
            self.assertEquals(address.get('zip', None), '94120-7704')

    def test_us_territory_irs_payment_address(self):
        states = (
            ('AS', 'American Samoa'),
            ('GU', 'Guam'),
            ('MP', 'Northern Mariana Islands'),
            ('PR', 'Puerto Rico'),
            ('VI', 'Virgin Islands'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]

            address = self.eightythreeb.irs_payment_address
            self.assertEquals(address.get('address1', None), 'Internal Revenue Service')
            self.assertEquals(address.get('address2', None), 'P.O. Box 1303')
            self.assertEquals(address.get('city', None), 'Charlotte')
            self.assertEquals(address.get('state', None), 'NC')
            self.assertEquals(address.get('zip', None), '28201-1303')
            self.assertEquals(address.get('country', None), 'USA')

    def test_international_irs_payment_address(self):
        del(self.eightythreeb.data['state'])

        address = self.eightythreeb.irs_payment_address
        self.assertEquals(address.get('address1', None), 'Internal Revenue Service')
        self.assertEquals(address.get('address2', None), 'P.O. Box 1303')
        self.assertEquals(address.get('city', None), 'Charlotte')
        self.assertEquals(address.get('state', None), 'NC')
        self.assertEquals(address.get('zip', None), '28201-1303')
        self.assertEquals(address.get('country', None), 'USA')


class IRSSpouseTest(BaseScenarios, TestCase):
    def setUp(self):
        super(IRSSpouseTest, self).setUp()
        self.basic_workspace()

    def test_in_spousal_state(self):
        states = (
            ('AZ', 'Arizona'),
            ('CA', 'California'),
            ('ID', 'Idaho'),
            ('LA', 'Louisiana'),
            ('NV', 'Nevada'),
            ('NM', 'New Mexico'),
            ('TX', 'Texas'),
            ('WA', 'Washington'),
            ('WI', 'Wisconsin'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]
            self.assertTrue(self.eightythreeb.customer_in_spousal_state)

    def test_not_in_spousal_state(self):
        states = (
            ('AL', 'Alabama'),
            ('AK', 'Alaska'),
            ('AR', 'Arkansas'),
            ('CO', 'Colorado'),
            ('CT', 'Connecticut'),
            ('DE', 'Delaware'),
            ('DC', 'District of Columbia'),
            ('FL', 'Florida'),
            ('GA', 'Georgia'),
            ('HI', 'Hawaii'),
            ('IL', 'Illinois'),
            ('IN', 'Indiana'),
            ('IA', 'Iowa'),
            ('KS', 'Kansas'),
            ('KY', 'Kentucky'),
            ('ME', 'Maine'),
            ('MD', 'Maryland'),
            ('MA', 'Massachusetts'),
            ('MI', 'Michigan'),
            ('MN', 'Minnesota'),
            ('MS', 'Mississippi'),
            ('MO', 'Missouri'),
            ('MT', 'Montana'),
            ('NE', 'Nebraska'),
            ('NH', 'New Hampshire'),
            ('NJ', 'New Jersey'),
            ('NY', 'New York'),
            ('NC', 'North Carolina'),
            ('ND', 'North Dakota'),
            ('OH', 'Ohio'),
            ('OK', 'Oklahoma'),
            ('OR', 'Oregon'),
            ('PA', 'Pennsylvania'),
            ('RI', 'Rhode Island'),
            ('SC', 'South Carolina'),
            ('SD', 'South Dakota'),
            ('TN', 'Tennessee'),
            ('UT', 'Utah'),
            ('VT', 'Vermont'),
            ('VA', 'Virginia'),
            ('WV', 'West Virginia'),
            ('WY', 'Wyoming'),

            # Non-state territories
            ('AS', 'American Samoa'),
            ('GU', 'Guam'),
            ('MP', 'Northern Mariana Islands'),
            ('PR', 'Puerto Rico'),
            ('VI', 'Virgin Islands'),
        )
        for s in states:
            self.eightythreeb.data['state'] = s[0]
            self.assertFalse(self.eightythreeb.customer_in_spousal_state)

    def test_spouse_must_sign(self):
        # No spouse + non-spousal state
        self.eightythreeb.data['has_spouse'] = False
        self.eightythreeb.data['state'] = 'AS'
        self.assertFalse(self.eightythreeb.spouse_must_sign)

        # No spouse + spousal state
        self.eightythreeb.data['has_spouse'] = False
        self.eightythreeb.data['state'] = 'CA'
        self.assertFalse(self.eightythreeb.spouse_must_sign)

        # Spouse and + non-spousal state
        self.eightythreeb.data['has_spouse'] = True
        self.eightythreeb.data['state'] = 'AS'
        self.assertFalse(self.eightythreeb.spouse_must_sign)

        # Spouse and + spousal state
        self.eightythreeb.data['has_spouse'] = True
        self.eightythreeb.data['state'] = 'CA'
        self.assertTrue(self.eightythreeb.spouse_must_sign)
