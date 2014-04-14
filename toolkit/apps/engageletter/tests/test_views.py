# -*- coding: utf-8 -*-
"""
"""
from django.core.urlresolvers import reverse
from toolkit.casper.workflow_case import BaseProjectCaseMixin, PyQueryMixin

from model_mommy import mommy

from toolkit.apps.workspace.tests.test_lawyer_markers import REQUIRED_MARKERS

from .data import ENGAGELETTER_DATA as BASE_ENGAGELETTER_DATA
from ..models import EngagementLetter
from ..views import SetupEngagementLetterTemplateView


class SetupEngagementLetterTemplateViewTest(BaseProjectCaseMixin):
    """
    Specifically test the crazy uppercase lowercase domain
    https://code.djangoproject.com/ticket/21837
    """
    def setUp(self):
        super(SetupEngagementLetterTemplateViewTest, self).setUp()
        self.basic_workspace();
        self.tool = mommy.make('engageletter.EngagementLetter',
                    slug='d1c545082d1241849be039e338e47aa0',
                    workspace=self.workspace,
                    user=self.user,
                    data=BASE_ENGAGELETTER_DATA.copy(),
                    status=EngagementLetter.STATUS.lawyer_complete_form)
        self.url = reverse('engageletter:lawyer_template', kwargs={'slug': self.tool.slug})

    def test_lawyer_template_view_authenticated(self):
        """
        must be logged in
        """
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.redirect_chain, [('http://testserver/start/?next=/engagement-letters/d1c545082d1241849be039e338e47aa0/template/lawyer/', 302)])

    def test_lawyer_template_view(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.url)

        self.assertEqual(type(resp.context_data.get('view')), SetupEngagementLetterTemplateView)
        self.assertEqual(resp.context_data.get('form').fields.keys(), ['body'])
        self.assertEqual(resp.template_name, ['engageletter/setup_engageletter_form.html'])
        # test template data
        self.assertEqual(resp.context_data['form'].initial.get('body'), self.tool.template_source('engageletter/doc/body.html'))


class LawyerCreateLetterWithoutTemplateSetText(PyQueryMixin, BaseProjectCaseMixin):
    """
    when the lawyer has not setup a template then the first step before creating
    a letter should be to fill in the template form
    """
    def setUp(self):
        super(LawyerCreateLetterWithoutTemplateSetText, self).setUp()
        self.basic_workspace();
        self.client.login(username=self.lawyer.username, password=self.password)

    def test_create_url(self):
        """
        create_url should be to the letterhead setup
        """

        url = reverse('workspace:tool_object_list', kwargs={'workspace': self.workspace.slug, 'tool': 'engagement-letters'})
        expected_url = '/me/settings/letterhead/?next=/workspace/lawpal-test/tool/engagement-letters/create/'

        resp = self.client.get(url)

        self.assertTrue('create_url' in resp.context_data)
        self.assertEqual(resp.context_data.get('create_url'), expected_url)

        # check the links are present
        html = self.pq(resp.content)
        create_links = html('a.create-tool')
        self.assertEqual(len(create_links), 2)
        for a in create_links:
            self.assertEqual(a.attrib['href'], expected_url)


class LawyerCreateLetterWithTemplateSetText(PyQueryMixin, BaseProjectCaseMixin):
    """
    when a lawyer has the REQUIRED_MARKERS set in their profile then the create_url
    should be the engageletter url
    """
    def setUp(self):
        super(LawyerCreateLetterWithTemplateSetText, self).setUp()
        self.basic_workspace();

        #
        # Set the values in the profile that will allow us to create a new
        # engagement letter
        #
        profile_data = self.lawyer.profile.data

        for k in REQUIRED_MARKERS:
            profile_data[k] = 'some value here'

        profile = self.lawyer.profile
        profile.data = profile_data
        profile.save(update_fields=['data'])

        self.client.login(username=self.lawyer.username, password=self.password)

    def test_create_url(self):
        """
        create_url should be to the letterhead setup
        """

        url = reverse('workspace:tool_object_list', kwargs={'workspace': self.workspace.slug, 'tool': 'engagement-letters'})
        expected_url = '/workspace/lawpal-test/tool/engagement-letters/create/'

        resp = self.client.get(url)

        self.assertTrue('create_url' in resp.context_data)
        self.assertEqual(resp.context_data.get('create_url'), expected_url)

        # check the links are present
        html = self.pq(resp.content)
        create_links = html('a.create-tool')
        self.assertEqual(len(create_links), 2)
        for a in create_links:
            self.assertEqual(a.attrib['href'], expected_url)
