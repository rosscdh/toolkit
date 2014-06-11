# -*- coding: utf-8 -*-
import json
import mock

from django.core.urlresolvers import reverse
from django.test import TestCase

from toolkit.casper.workflow_case import BaseScenarios


class TwoFactorDisableViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(TwoFactorDisableViewTest, self).setUp()
        self.basic_workspace()

        profile = self.lawyer.profile
        profile.data['two_factor_enabled'] = True
        profile.save()

    def test_disable_two_factor(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        response = self.client.post(
            reverse('me:two-factor-disable'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/me/settings/')
        self.assertFalse(self.lawyer.profile.data.get('two_factor_enabled'))


class TwoFactorEnableViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(TwoFactorEnableViewTest, self).setUp()
        self.basic_workspace()

    def test_enable_two_factor(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        response = self.client.post(
            reverse('me:two-factor-enable'),
            {
                'cellphone': 7800000000,
                'country': 44,
                'is_smartphone': True,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'modal': True,
            'target': '#verify-two-factor',
            'url': reverse('me:two-factor-verify')
        })


class TwoFactorVerifyViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(TwoFactorVerifyViewTest, self).setUp()
        self.basic_workspace()

        authy_profile = self.lawyer.authy_profile
        authy_profile.authy_id = 1
        authy_profile.cellphone = '+440000000000'
        authy_profile.save()

    @mock.patch('dj_authy.services.AuthyService.verify_token')
    @mock.patch('dj_authy.services.AuthyService.ensure_user_registered')
    def test_verify_two_factor(self, verify_token_mock, ensure_user_mock):
        self.client.login(username=self.lawyer.username, password=self.password)

        response = self.client.post(reverse('me:two-factor-verify'), {'token': '0000000'})
        self.assertEqual(verify_token_mock.call_count, 1)
        self.assertEqual(response.status_code, 200)
        # json response for popup window
        self.assertEqual(response.content, '{"redirect": true, "url": "/me/settings/"}')

        self.assertTrue(self.lawyer.profile.data.get('two_factor_enabled'))
