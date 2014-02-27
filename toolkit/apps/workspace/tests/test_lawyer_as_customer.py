# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

from toolkit.casper import BaseScenarios
from toolkit.apps.eightythreeb.forms import LawyerEightyThreeBForm, CustomerEightyThreeBForm
from toolkit.apps.workspace.views import CreateToolObjectView, UpdateViewToolObjectView, DeleteToolObjectView


class LawyerAsLawyerTest(BaseScenarios, TestCase):
    """
    Test that the lawyer views the appropriate views and forms when creating and
    editing a tool
    """
    def setUp(self):
        super(LawyerAsLawyerTest, self).setUp()
        self.basic_workspace()
        # login as the lawyer
        self.client.login(username=self.lawyer.username, password=self.password)

    def test_tool_form_create(self):
        """
        The Lawyer when creating a form, should see the Lawyer version of the
        form
        """
        resp = self.client.get(reverse('workspace:tool_object_new', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug}), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(type(resp.context_data.get('view')), CreateToolObjectView)
        self.assertEqual(type(resp.context_data.get('form')), LawyerEightyThreeBForm)


    def test_view_tool_form_edit(self):
        """
        The Lawyer should always see the Lawyer Version of the form
        """
        resp = self.client.get(reverse('workspace:tool_object_edit', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug, 'slug': self.eightythreeb.slug}), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(type(resp.context_data.get('view')), UpdateViewToolObjectView)
        self.assertEqual(type(resp.context_data.get('form')), LawyerEightyThreeBForm)

    def test_view_tool_form_delete(self):
        """
        The Lawyer should always be allowed to delete
        """
        resp = self.client.get(reverse('workspace:tool_object_delete', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug, 'slug': self.eightythreeb.slug}), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(type(resp.context_data.get('view')), DeleteToolObjectView)

    def test_view_tool_get_form_key(self):
        """
        The Lawyer should always see the LAwyer version of the form
        """
        create_resp = self.client.get(reverse('workspace:tool_object_new', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug}), follow=True)
        self.assertEqual(create_resp.context_data.get('view').get_form_key(), None)

        edit_resp = self.client.get(reverse('workspace:tool_object_edit', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug, 'slug': self.eightythreeb.slug}), follow=True)
        self.assertEqual(edit_resp.context_data.get('view').get_form_key(), None)


class LawyerAsCustomerTest(BaseScenarios, TestCase):
    """
    Test that should a lawyer account be assigned as the CUSTOMER then they should
    see the customer Form and View when editing the tool
    """
    def setUp(self):
        super(LawyerAsCustomerTest, self).setUp()
        self.basic_workspace()
        # set user to be the lawyer
        self.eightythreeb.user = self.lawyer
        self.eightythreeb.save(update_fields=['user'])
        # login as the lawyer
        self.client.login(username=self.lawyer.username, password=self.password)

    def test_tool_form_create(self):
        """
        The Lawyer when creating a form, should see the Lawyer version of the
        form
        """
        resp = self.client.get(reverse('workspace:tool_object_new', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug}), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(type(resp.context_data.get('view')), CreateToolObjectView)
        self.assertEqual(type(resp.context_data.get('form')), LawyerEightyThreeBForm)


    def test_view_tool_form_edit(self):
        """
        The Lawyer when editing their form, should then see the customer form
        version of the form
        """
        resp = self.client.get(reverse('workspace:tool_object_edit', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug, 'slug': self.eightythreeb.slug}), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(type(resp.context_data.get('view')), UpdateViewToolObjectView)
        self.assertEqual(type(resp.context_data.get('form')), CustomerEightyThreeBForm)

    def test_view_tool_get_form_key(self):
        """
        Test the get_form_key method which returns a dict key used to extract
        the form type in the view
        """
        create_resp = self.client.get(reverse('workspace:tool_object_new', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug}), follow=True)
        self.assertEqual(create_resp.context_data.get('view').get_form_key(), None)

        edit_resp = self.client.get(reverse('workspace:tool_object_edit', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug, 'slug': self.eightythreeb.slug}), follow=True)
        self.assertEqual(edit_resp.context_data.get('view').get_form_key(), 'customer')
