# -*- coding: utf-8 -*-
from django.core import mail
from django.core import signing
from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.messages import get_messages

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.casper.workflow_case import BaseScenarios

from ..forms import (ChangePasswordForm, AccountSettingsForm)


def _get_action_url(url_name, user):
    token = signing.dumps(user.pk, salt=settings.URL_ENCODE_SECRET_KEY)
    # remove teh token; because signing creates a token with datetime invlved
    # and tometimes out tests woudl fail because of the time diff involved in
    # the testing process; so simply generate teh url but remove the token so
    # at least we guarantee that the url is in the body
    return ABSOLUTE_BASE_URL(reverse(url_name, kwargs={'token': token})).replace(token, '')


class AccountPasswordChangeTest(BaseScenarios, TestCase):
    subject = ChangePasswordForm

    def setUp(self):
        self.basic_workspace()
        self.url = reverse('me:change-password')

    def test_password_change_requires_validation(self):
        self.client.login(username=self.user.username, password=self.password)

        expected_original_password = self.user.password

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        form = resp.context_data.get('form')
        self.assertEqual(form.__class__.__name__, 'ChangePasswordForm')
        self.assertEqual(form.rendered_fields, set([u'new_password2', u'new_password1']))

        form_data = form.initial
        form_data.update({
            'new_password1': 'bananas',
            'new_password2': 'bananas',
            'csrfmiddlewaretoken': unicode(resp.context['csrf_token']),
        })

        resp = self.client.post(self.url, form_data, follow=True)
        # get action url in email
        expected_action_url = _get_action_url('me:confirm-password-change', self.user)

        self.assertEqual(resp.status_code, 200)
        # test they were logged out
        self.assertTrue('_auth_user_id' not in self.client.session)

        # test the temp variable was set
        self.assertTrue('validation_required_temp_password' in self.user.profile.data)
        # and that the passwords are not the same
        self.assertNotEqual(expected_original_password, self.user.profile.data['validation_required_temp_password'])
        # test users password has not been changes
        self.assertEqual(expected_original_password, self.user.password)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, u'Please confirm your change of password')
        #self.assertTrue(expected_action_url in unicode(email.body))

        # test that the password gets reset when we visit this url
        resp = self.client.get(expected_action_url, follow=True)
        self.assertEqual(resp.redirect_chain, [('http://testserver/', 301)])

        self.user = self.user.__class__.objects.get(pk=self.user.pk)  # refresh

        # test they were not logged in
        self.assertTrue('_auth_user_id' not in self.client.session)

        self.assertTrue('validation_required_temp_password' not in self.user.profile.data)
        self.assertNotEqual(expected_original_password, self.user.password)
        self.assertTrue('Congratulations. Your password has been changed. Please login with your new password.' in resp.content)


class AccountEmailChangeTest(BaseScenarios, TestCase):
    """
    Test teh changing of an email
    """
    subject = AccountSettingsForm

    def setUp(self):
        self.basic_workspace()
        self.url = reverse('me:settings')

    def test_email_change_requires_validation(self):
        self.client.login(username=self.user.username, password=self.password)

        expected_original_email = self.user.email

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        form = resp.context_data.get('form')
        self.assertEqual(form.__class__.__name__, 'AccountSettingsForm')
        self.assertEqual(form.rendered_fields, set([u'first_name', u'last_name', u'email']))

        form_data = form.initial
        form_data.update({
            'email': 'change_of_email_test@lawpal.com',
            'csrfmiddlewaretoken': unicode(resp.context['csrf_token']),
        })

        resp = self.client.post(self.url, form_data, follow=True)
        # get action url in email
        expected_action_url = _get_action_url('me:confirm-email-change', self.user)
        self.assertEqual(resp.status_code, 200)

        # test the temp variable was set
        self.assertTrue('validation_required_temp_email' in self.user.profile.data)
        # test that their account email needs to be revalidated
        self.assertTrue(self.user.profile.validated_email is False)
        # and that the passwords are not the same
        self.assertNotEqual(expected_original_email, self.user.profile.data['validation_required_temp_email'])
        # test users password has not been changes
        self.assertEqual(expected_original_email, self.user.email)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, u'Please confirm your change of email address')
        # print email.body
        # print expected_action_url
        #self.assertTrue(expected_action_url in unicode(email.body))

        # test that the password gets reset when we visit this url
        resp = self.client.get(expected_action_url, follow=True)
        # because the user can remain logged in they are redirected to / and then to /matters
        self.assertEqual(resp.redirect_chain, [('http://testserver/', 301)])

        self.user = self.user.__class__.objects.get(pk=self.user.pk)  # refresh

        # test they were not logged in
        self.assertTrue('_auth_user_id' not in self.client.session)
        # test the marker was deleted
        self.assertTrue('validation_required_temp_email' not in self.user.profile.data)
        # test that their account email has been validated
        self.assertTrue(self.user.profile.validated_email is True)
        self.assertNotEqual(expected_original_email, self.user.email)
        self.assertTrue('Congratulations. Your email has been changed. Please login with your new email.' in resp.content)

    def test_email_cant_change_to_existing_user(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.get(self.url)
        form = resp.context_data.get('form')

        form_data = form.initial
        form_data.update({
            'email': self.lawyer.email,  # Try to use another users email address
            'csrfmiddlewaretoken': unicode(resp.context['csrf_token']),
        })

        resp = self.client.post(self.url, form_data, follow=True)
        # shoudl show form again with error message
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['user/settings/account.html'])
        self.assertTrue('An account with that email already exists.' in resp.content)
