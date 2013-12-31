# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseProjectCaseMixin
from toolkit.apps.workspace.models import Tool


class BaseCustomer(BaseProjectCaseMixin):
    def setUp(self):
        super(BaseCustomer, self).setUp()
        self.basic_workspace()
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
        test invite url logs user in
        """
        resp = self.client.get(self.invite.get_absolute_url(), follow=True)
        self.assertEqual(resp.status_code, 200)
        import pdb;pdb.set_trace()


class CustomerInviteLoginRedirectTest(TestCase):
    pass