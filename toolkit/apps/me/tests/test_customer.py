# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseProjectCaseMixin
from toolkit.apps.workspace.models import Tool
from toolkit.apps.me.forms import ConfirmAccountForm
from toolkit.apps.workspace.views import ToolObjectPreviewView
from toolkit.apps.matter.views import MatterListView


class BaseCustomer(BaseProjectCaseMixin):
    def setUp(self):
        super(BaseCustomer, self).setUp()
        self.basic_workspace()

        # reset userpass
        self.user.password = ''
        self.user.save(update_fields=['password'])

        self.invite = mommy.make('workspace.InviteKey', invited_user=self.user,
                                 inviting_user=self.lawyer,
                                 tool=Tool.objects.get(slug='83b-election-letters'),
                                 tool_object_id=self.eightythreeb.pk,
                                 next=self.eightythreeb.get_absolute_url())


class CustomerInviteLoginTest(BaseCustomer):
    """
    As a customer
    when i get an invite url
    I should be able to login and directly use the system
    """
    def setUp(self):
        super(CustomerInviteLoginTest, self).setUp()

        self.confirm_account_url = reverse('me:confirm-account')  # account confirm page not normal password reset page

        self.resp = self.client.get(self.invite.get_absolute_url(), follow=True)

        self.assertEqual(len(self.resp.redirect_chain), 2)
        self.assertEqual(self.resp.redirect_chain[1], ('http://testserver%s' % self.confirm_account_url, 302))

        self.assertEqual(type(self.resp.context_data.get('form')), ConfirmAccountForm)
        self.assertEqual(self.resp.context_data.get('user'), self.user)
        self.assertEqual(self.resp.context_data.get('object'), self.user)

    def submit_confirm_account_form(self, resp):
        # test submit of form
        form_data = resp.context_data['form'].initial
        form_data.update({
            'new_password1': 'password',
            'new_password2': 'password',
            'csrfmiddlewaretoken': unicode(resp.context['csrf_token']),
        })
        return self.client.post(self.confirm_account_url, form_data, follow=True)

    def test_invited_login(self):
        """
        Customer invited and has no password set
        is redirected to confirm account page
        """
        self.assertTrue('sent_welcome_email' not in self.user.profile.data)

        formsubmit_resp = self.submit_confirm_account_form(resp=self.resp)
        # is on the right view
        self.assertEqual(type(formsubmit_resp.context_data.get('view')), ToolObjectPreviewView)
        # has the sent welcome message key set
        self.assertTrue('sent_welcome_email' in self.user.profile.data)
        # Test email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Welcome to LawPal')
        self.assertEqual(email.recipients(), [self.user.email])
        self.assertEqual(email.from_email, 'support@lawpal.com')
        self.assertEqual(email.extra_headers, {'Reply-To': 'support@lawpal.com'})


    def test_welcome_email_sent_with_no_invitation_record(self):
        """
        Customer is unconfirmed account
        with no invite record
        will be sent_welcome_email is in the users profile.data
        is redirected to homepage on submit
        """
        # delete invite
        self.user.invitations.all().delete()

        formsubmit_resp = self.submit_confirm_account_form(resp=self.resp)

        # is on the right view
        self.assertEqual(type(formsubmit_resp.context_data.get('view')), MatterListView)
        self.assertTrue(self.workspace in formsubmit_resp.context_data['workspace_list'])
        
        # has the sent welcome message key set
        self.assertTrue('sent_welcome_email' in self.user.profile.data)
        # Test email
        self.assertEqual(len(mail.outbox), 1)  # an email was sent

    def test_cant_access_confirm_account_form_with_confirmed_account(self):
        """
        Customer has set password and is confirmed
        is redirected to homepage on submit on attempted access
        """
        profile = self.user.profile
        profile.data['sent_welcome_email'] = True
        profile.save(update_fields=['data'])

        self.user.set_password('test')
        self.user.save(update_fields=['password'])

        # POST access is redirected
        formsubmit_resp = self.submit_confirm_account_form(resp=self.resp)
        self.assertEqual(len(formsubmit_resp.redirect_chain), 2)

        # normal GET access is redirected
        resp = self.client.get(self.invite.get_absolute_url(), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        self.assertTrue(resp.context_data.get('form') is None)
