# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse

from django.test import TestCase

from toolkit.apps.workspace.models import Workspace
from toolkit.casper.workflow_case import BaseScenarios

from ..views import MatterDetailView


class MatterListViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterListViewTest, self).setUp()
        self.basic_workspace()

    def test_queryset(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        res = self.client.get(reverse('matter:list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['object_list']), Workspace.objects.mine(self.lawyer).count())

    def test_redirects_to_login_if_not_logged_in(self):
        # User not logged in
        response = self.client.get(reverse('matter:list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/start/?next=/matters/')


class MatterDetailViewTest(TestCase):
    subject = MatterDetailView

    def test_get_template_names_dev(self):
        with self.settings(PROJECT_ENVIRONMENT='prod'):
            subject = self.subject()
            self.assertEqual(subject.get_template_names(), ['dist/index.html'])
        #
        # in prod even with debug True we should not see the debug gui
        #
        with self.settings(PROJECT_ENVIRONMENT='prod', DEBUG=True):
            subject = self.subject()
            self.assertEqual(subject.get_template_names(), ['dist/index.html'])

    def test_get_template_names_prod(self):
        with self.settings(PROJECT_ENVIRONMENT='dev', DEBUG=True):
            subject = self.subject()
            self.assertEqual(subject.get_template_names(), ['index.html'])

        #
        # We should be able to test how it would look in production
        # from within the dev environment
        #
        with self.settings(PROJECT_ENVIRONMENT='dev', DEBUG=False):
            subject = self.subject()
            self.assertEqual(subject.get_template_names(), ['dist/index.html'])


class MatterCreateViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterCreateViewTest, self).setUp()
        self.basic_workspace()

    def test_valid_form(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        url = reverse('matter:create')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            'client_name': 'Acme Inc',
            'name': 'Incorporation & Financing'
        }
        response = self.client.post(url, post_data, follow=True)

        #
        # assume the post worked
        #
        matter = Workspace.objects.get(slug='incorporation-financing')

        actual_response = {
            'redirect': True,
            'url': matter.get_absolute_url()
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps(actual_response))

    def test_valid_form_with_matter_template(self):
        template_matter = Workspace.objects.get(pk=1)

        self.client.login(username=self.lawyer.username, password=self.password)

        url = reverse('matter:create')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            'client_name': 'Acme Inc',
            'name': 'Incorporation & Financing',
            'template': template_matter.pk,
        }
        response = self.client.post(url, post_data, follow=True)

        #
        # assume the post worked
        #
        matter = Workspace.objects.get(slug='incorporation-financing')

        actual_response = {
            'redirect': True,
            'url': matter.get_absolute_url()
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps(actual_response))

    def test_redirects_to_login_if_not_logged_in(self):
        # User not logged in
        response = self.client.get(reverse('matter:create'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/start/?next=/matters/create/')


class MatterUpdateViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterUpdateViewTest, self).setUp()
        self.basic_workspace()

    def test_valid_form(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        url = reverse('matter:edit', kwargs={'matter_slug': self.workspace.slug})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            'client_name': 'Acme Inc',
            'name': 'Incorporation & Financing'
        }
        response = self.client.post(url, post_data, follow=True)

        actual_response = {
            'redirect': True,
            'url': reverse('matter:list')
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps(actual_response))

    def test_redirects_to_login_if_not_logged_in(self):
        # User not logged in
        response = self.client.get(reverse('matter:edit', kwargs={'matter_slug': self.workspace.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/start/?next=/matters/lawpal-test/edit/')


class MatterDeleteViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterDeleteViewTest, self).setUp()
        self.basic_workspace()

    def test_valid_form(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        url = reverse('matter:delete', kwargs={'matter_slug': self.workspace.slug})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/matters/')

        # test the matter is deleted
        with self.assertRaises(Workspace.DoesNotExist):
            Workspace.objects.get(pk=self.workspace.pk)

    def test_redirects_to_login_if_not_logged_in(self):
        # User not logged in
        response = self.client.get(reverse('matter:delete', kwargs={'matter_slug': self.workspace.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/start/?next=/matters/lawpal-test/delete/')
