# -*- coding: utf-8 -*-
"""
Test the user can signup with a crazy none RFC valid email address
Test the user can signin with the saem crazy email address
Note that the DB will save as valid ie.. Crap@NortyStuff.com will be saved as Crap@nortystuff.com
"""
from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseProjectCaseMixin
#from toolkit.apps.dash.views import DashView
from toolkit.apps.matter.views import MatterListView

class CustomerSignUpTest(BaseProjectCaseMixin):
    """
    Specifically test the crazy uppercase lowercase domain
    """
    def test_signup(self):
        url = reverse('public:signup')
        resp = self.client.get(url)

        self.assertEqual(resp.context_data.get('form').fields.keys(), ['username', 'firm_name', 'first_name', 'last_name', 'email', 'password', 'password_confirm', 't_and_c', 'mpid'])

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'username': None,
            'firm_name': 'Test Firm Inc.',
            'first_name': 'Monkey',
            'last_name': 'Tester',
            'email': 'MySillyUserName@BadlyFormatedEmailNonRFCDomain.com',
            'password': 'password',
            'password_confirm':'password',
            't_and_c': True,
            'csrfmiddlewaretoken': unicode(resp.context['csrf_token']),
        })

        form_resp = self.client.post(url, form_data, follow=True)

        # is logged in
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(form_resp.context['user'].is_authenticated(), True)

        # of this user
        self.assertEqual(form_resp.context['user'].username, 'mysillyusername')
        self.assertEqual(form_resp.context['user'].email, 'MySillyUserName@badlyformatedemailnonrfcdomain.com')
        # redirected to DashView
        self.assertEqual(type(form_resp.context_data.get('view')), MatterListView)


class CustomerSignInTest(BaseProjectCaseMixin):
    """
    Specifically test the crazy uppercase lowercase domain
    """
    def setUp(self):
        super(CustomerSignInTest, self).setUp()
        self.user = mommy.make('auth.User', username='mysillyusername', first_name='Monkey', last_name='Tester', email='MySillyUserName@badlyformatedemailnonrfcdomain.com')
        self.user.set_password('password')
        self.user.save()

    def test_signin(self):
        url = reverse('public:signin')
        resp = self.client.get(url)

        self.assertEqual(resp.context_data.get('form').fields.keys(), ['email', 'password'])

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'email': 'MySillyUserName@BadlyFormatedEmailNonRFCDomain.com',
            'password': 'password',
        })

        form_resp = self.client.post(url, form_data, follow=True)

        # of this user
        self.assertEqual(form_resp.context['user'].is_authenticated(), True)
        self.assertEqual(form_resp.context['user'].username, 'mysillyusername')
        self.assertEqual(form_resp.context['user'].email, 'MySillyUserName@badlyformatedemailnonrfcdomain.com')
        # redirected to DashView
        self.assertEqual(type(form_resp.context_data.get('view')), MatterListView)
