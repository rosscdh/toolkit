# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse

from toolkit.casper import BaseScenarios
from toolkit.apps.workspace.views import InviteClientToolObjectView, ToolObjectPreviewView
from toolkit.apps.workspace.forms import InviteUserForm


class InviteCustomerTest(BaseScenarios, TestCase):
    """
    Test that the lawyer views the appropriate views and forms when creating and
    editing a tool
    """
    def setUp(self):
        super(InviteCustomerTest, self).setUp()
        self.basic_workspace()
        # login as the lawyer
        self.client.login(username=self.lawyer.username, password=self.password)

    def test_mail_sent(self):
        """
        The Lawyer when creating a form, should see the Lawyer version of the
        form
        """
        invite_url = reverse('workspace:tool_object_invite', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug='83b-election-letters').first().slug, 'slug': self.eightythreeb.slug})

        resp = self.client.get(invite_url, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(type(resp.context_data.get('view')), InviteClientToolObjectView)
        self.assertEqual(type(resp.context_data.get('form')), InviteUserForm)

        form = resp.context_data.get('form')
        required_fields = {
            'subject': form.get_initial_subject(),
            'message': form.get_initial_message(),
        }
        # ensure our required fields are in the form
        for field_name in required_fields.keys():
            self.assertTrue(field_name in form.fields)
            # ensure is required
            self.assertTrue(form.fields[field_name].required)
            # test the value
            self.assertTrue(form.fields[field_name].initial == required_fields[field_name])

        form_data = form.initial
        form_data.update(required_fields)

        form_resp = self.client.post(invite_url, form_data, follow=True)
        self.assertEqual(form_resp.status_code, 200)
        # redirects to the workspace preview
        self.assertEqual(type(form_resp.context_data.get('view')), ToolObjectPreviewView)

        # test email is sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, required_fields.get('subject'))
        self.assertEqual(email.recipients(), [self.user.email])
        self.assertEqual(email.from_email, u'Lawyër Tëst (via LawPal) support@lawpal.com')
        self.assertEqual(email.extra_headers, {'Reply-To': self.lawyer.email})
