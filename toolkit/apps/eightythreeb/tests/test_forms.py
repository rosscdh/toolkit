# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
from toolkit.casper.workflow_case import BaseScenarios, PyQueryMixin

from ..forms import CustomerEightyThreeBForm, LawyerEightyThreeBForm


class CustomerEightyThreeBFormTest(BaseScenarios, PyQueryMixin, TestCase):
    def setUp(self):
        super(CustomerEightyThreeBFormTest, self).setUp()
        self.basic_workspace()
        self.client.login(username=self.user.username, password=self.password)

        self.expected_fields = ['client_full_name',
                                'client_email',
                                'company_name',
                                'address1',
                                'address2',
                                'city',
                                'state',
                                'post_code',
                                'ssn',
                                'itin',
                                'accountant_email',
                                'has_spouse',
                                'date_of_property_transfer',
                                'description',
                                'tax_year',
                                'nature_of_restrictions',
                                'transfer_value_share',
                                'total_shares_purchased',
                                'price_paid_per_share',
                                'disclaimer_agreed',
                                'details_confirmed']

        self.disabled = []
        self.readonly = []

    def test_fields(self):
        url = reverse('workspace:tool_object_edit', kwargs={'workspace': self.workspace.slug, 'tool': self.eightythreeb.tool_slug, 'slug': self.eightythreeb.slug})
        resp = self.client.get(url)

        form = resp.context_data.get('form')
        self.assertEqual(type(form), CustomerEightyThreeBForm)
        self.assertEqual(form.fields.keys(), self.expected_fields)

        html = self.pq(resp.content)
        for f in self.expected_fields:
            field_id = '#id_%s' % f
            attrs = form.fields[f].widget.attrs.keys()

            if 'readonly' in attrs or 'disabled' in attrs:
                self.fail('There should be no readonly or disabled widgets in the CustomerEightyThreeBForm')
            else:
                self.assertEqual(len(html(field_id)), 1)


class LawyerEightyThreeBFormTest(BaseScenarios, PyQueryMixin, TestCase):
    def setUp(self):
        super(LawyerEightyThreeBFormTest, self).setUp()
        self.basic_workspace()
        self.client.login(username=self.lawyer.username, password=self.password)

        self.expected_fields = ['client_full_name',
                                'client_email',
                                'company_name',
                                'address1',
                                'address2',
                                'city',
                                'state',
                                'post_code',
                                'ssn',
                                'itin',
                                'accountant_email',
                                'has_spouse',
                                'date_of_property_transfer',
                                'description',
                                'tax_year',
                                'nature_of_restrictions',
                                'transfer_value_share',
                                'total_shares_purchased',
                                'price_paid_per_share',
                                #'disclaimer_agreed',
                                #'details_confirmed'
                                ]
        self.disabled = ['state', 'has_spouse']
        self.readonly = ['address1', 'address2', 'city', 'post_code', 'ssn', 'itin', 'accountant_email']

    def test_fields(self):
        url = reverse('workspace:tool_object_edit', kwargs={'workspace': self.workspace.slug, 'tool': self.eightythreeb.tool_slug, 'slug': self.eightythreeb.slug})
        resp = self.client.get(url)

        form = resp.context_data.get('form')
        self.assertEqual(type(form), LawyerEightyThreeBForm)
        self.assertEqual(form.fields.keys(), self.expected_fields)

        html = self.pq(resp.content)
        for f in self.expected_fields:
            field_id = '#id_%s' % f
            attrs = form.fields[f].widget.attrs.keys()

            if 'readonly' in attrs or 'disabled' in attrs:
                if 'readonly' in attrs:
                    self.assertTrue(f in self.readonly)
                    self.assertTrue(f not in self.disabled)
                else:
                    self.assertTrue(f not in self.readonly)
                    self.assertTrue(f in self.disabled)

                self.assertEqual(len(html(field_id)), 0)
            else:
                self.assertEqual(len(html(field_id)), 1)
