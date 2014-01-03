# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseProjectCaseMixin
from toolkit.apps.workspace.models import Tool


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
    def test_invited_login(self):
        """
        Customer invited and has no pasword set
        is redirected to confirm account page
        """
        resp = self.client.get(self.invite.get_absolute_url(), follow=True)
        self.assertEqual(len(resp.redirect_chain), 2)
        self.assertEqual(resp.redirect_chain[1], ('http://testserver%s' % reverse('me:confirm-account'), 302))

    def test_password_set_login(self):
        """
        Customer logs in after having set password
        is redirected to last invited object
        """
        self.user.set_password('test')
        self.user.save(update_fields=['password'])

        resp = self.client.get(self.invite.get_absolute_url(), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        # redirects to the eighty threeb (the last invite sent to this user object)
        self.assertEqual(resp.redirect_chain[0], ('http://testserver%s' % self.eightythreeb.get_absolute_url(), 302))
