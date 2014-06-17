# -*- coding: utf-8 -*-
import mock

from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from toolkit.apps.default import _get_unique_username
from toolkit.apps.matter.views import MatterListView, MatterDetailView
from toolkit.casper.workflow_case import BaseProjectCaseMixin

from .fields import HTMLField
from .views import VerifyTwoFactorView


class UniqueUsernameTest(TestCase):
    def setUp(self):
        super(UniqueUsernameTest, self).setUp()
        self.userA = mommy.make('auth.User', username='customerA', first_name='Customer', last_name='TestA', email='testA+customer@lawpal.com')

    def test__get_unique_username(self):
        self.assertEqual(_get_unique_username('unique-monkey-nuts'), 'unique-monkey-nuts')

    def test__get_unique_username_not_unique(self):
        self.assertNotEqual(_get_unique_username('customerA'), 'customerA')


class HTMLFieldTests(TestCase):
    def test_microsoft_word_html(self):
        # test that we strip Microsoft Word HTML
        f = HTMLField()
        self.assertEqual(f.to_python("<p class=MsoNormal style='margin-top:3.0pt;margin-right:0in;margin-bottom:0in;margin-left:.2in;margin-bottom:.0001pt;text-indent:-.2in'>Hello world!</p>"), 'Hello world!')
        self.assertEqual(f.to_python("<p style='margin-top:3.0pt;margin-right:0in;margin-bottom:0in;margin-left:.2in;margin-bottom:.0001pt;text-indent:-.2in'><a name=ahali></a><b>Hello</b> <i>[...]</i> world!</p>"), 'Hello [...] world!')


class TwoFactorSignInTest(BaseProjectCaseMixin):
    def setUp(self):
        super(TwoFactorSignInTest, self).setUp()
        self.user = mommy.make('auth.User', username='testuser', first_name='Monkey', last_name='Tester', email='foo@bar.com')
        self.user.set_password('password')
        self.user.save()

    @mock.patch('dj_authy.services.AuthyService.ensure_user_registered')
    @mock.patch('dj_authy.services.AuthyService.request_sms_token')
    @mock.patch('dj_authy.services.AuthyService.verify_token')
    def test_signin_with_two_factor_enabled(self, verify_token_mock, request_sms_token_mock, ensure_user_mock):
        profile = self.user.profile
        profile.data['two_factor_enabled'] = True
        profile.save(update_fields=['data'])

        authy_profile = self.user.authy_profile
        authy_profile.authy_id = 1
        authy_profile.cellphone = '+440000000000'
        authy_profile.save()

        url = reverse('public:signin')
        resp = self.client.get(url)

        request_sms_token_mock.return_value = True
        verify_token_mock.return_value = True

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'email': 'foo@bar.com',
            'password': 'password',
        })
        form_resp = self.client.post(url, form_data, follow=True)
        self.assertEqual(type(form_resp.context_data.get('view')), VerifyTwoFactorView)

        self.assertEqual(request_sms_token_mock.call_count, 1)
        self.assertEqual(verify_token_mock.call_count, 0)

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'token': '0000000',
        })
        form_resp = self.client.post(reverse('public:signin-two-factor'), form_data, follow=True)
        self.assertEqual(request_sms_token_mock.call_count, 1)
        self.assertEqual(verify_token_mock.call_count, 1)
        self.assertEqual(form_resp.context['user'].is_authenticated(), True)
        self.assertEqual(form_resp.context['user'].username, 'testuser')
        self.assertEqual(form_resp.context['user'].email, 'foo@bar.com')
        self.assertEqual(type(form_resp.context_data.get('view')), MatterListView)

    def test_signin_without_two_factor_enabled(self):
        url = reverse('public:signin')
        resp = self.client.get(url)

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'email': 'foo@bar.com',
            'password': 'password',
        })

        form_resp = self.client.post(url, form_data, follow=True)
        self.assertEqual(form_resp.context['user'].is_authenticated(), True)
        self.assertEqual(form_resp.context['user'].username, 'testuser')
        self.assertEqual(form_resp.context['user'].email, 'foo@bar.com')

        self.assertEqual(type(form_resp.context_data.get('view')), MatterListView)


class RedirectAfterLoginTest(BaseProjectCaseMixin):
    def setUp(self):
        super(RedirectAfterLoginTest, self).setUp()
        self.basic_workspace()

    @mock.patch('dj_authy.services.AuthyService.verify_token')
    @mock.patch('dj_authy.services.AuthyService.ensure_user_registered')
    def test_redirect_with_two_factor_enabled(self, verify_token_mock, ensure_user_mock):
        target_url = reverse('matter:detail', kwargs={'matter_slug': self.matter.slug})

        profile = self.lawyer.profile
        profile.data['two_factor_enabled'] = True
        profile.save(update_fields=['data'])

        authy_profile = self.user.authy_profile
        authy_profile.authy_id = 1
        authy_profile.cellphone = '+440000000000'
        authy_profile.save()

        resp = self.client.get(target_url, follow=True)

        verify_token_mock.return_value = True

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'email': 'test+lawyer@lawpal.com',
            'password': 'password',
        })
        form_resp = self.client.post(reverse('public:signin'), form_data, follow=True)
        self.assertEqual(type(form_resp.context_data.get('view')), VerifyTwoFactorView)

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'token': '0000000',
        })
        form_resp = self.client.post(reverse('public:signin-two-factor'), form_data, follow=True)
        self.assertEqual(verify_token_mock.call_count, 1)
        self.assertEqual(form_resp.context['user'].is_authenticated(), True)
        self.assertEqual(form_resp.context['user'].username, 'test-lawyer')
        self.assertEqual(form_resp.context['user'].email, 'test+lawyer@lawpal.com')
        self.assertEqual(type(form_resp.context_data.get('view')), MatterDetailView)

    def test_redirect_without_two_factor_enabled(self):
        target_url = reverse('matter:detail', kwargs={'matter_slug': self.matter.slug})

        resp = self.client.get(target_url, follow=True)

        form_data = resp.context_data.get('form').initial
        form_data.update({
            'email': 'test+lawyer@lawpal.com',
            'password': 'password',
        })

        form_resp = self.client.post(reverse('public:signin'), form_data, follow=True)
        self.assertEqual(form_resp.context['user'].is_authenticated(), True)
        self.assertEqual(form_resp.context['user'].username, 'test-lawyer')
        self.assertEqual(form_resp.context['user'].email, 'test+lawyer@lawpal.com')

        self.assertEqual(type(form_resp.context_data.get('view')), MatterDetailView)
