import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from toolkit.apps.workspace.models import Workspace
from toolkit.casper.workflow_case import BaseScenarios


class MatterListViewTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterListViewTestCase, self).setUp()
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


class MatterCreateViewTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterCreateViewTestCase, self).setUp()
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

        actual_response = {
            'redirect': True,
            'url': reverse('matter:detail', kwargs={'matter_slug': 'incorporation-financing'})
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps(actual_response))

    def test_redirects_to_login_if_not_logged_in(self):
        # User not logged in
        response = self.client.get(reverse('matter:create'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/start/?next=/matters/create/')


class MatterUpdateViewTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterUpdateViewTestCase, self).setUp()
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
            'url': reverse('matter:detail', kwargs={'matter_slug': self.workspace.slug})
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps(actual_response))

    def test_redirects_to_login_if_not_logged_in(self):
        # User not logged in
        response = self.client.get(reverse('matter:edit', kwargs={'matter_slug': self.workspace.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/start/?next=/matters/lawpal-test/edit/')


class MatterDeleteViewTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterDeleteViewTestCase, self).setUp()
        self.basic_workspace()

    def test_valid_form(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        url = reverse('matter:delete', kwargs={'matter_slug': self.workspace.slug})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {}, follow=True)

        actual_response = {
            'redirect': True,
            'url': reverse('matter:list')
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps(actual_response))

        # test the matter is deleted
        with self.assertRaises(Workspace.DoesNotExist):
            Workspace.objects.get(pk=self.workspace.pk)

    def test_redirects_to_login_if_not_logged_in(self):
        # User not logged in
        response = self.client.get(reverse('matter:delete', kwargs={'matter_slug': self.workspace.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/start/?next=/matters/lawpal-test/delete/')
