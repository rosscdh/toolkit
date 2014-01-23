# -*- coding: utf-8 -*-
"""
"""
from django.core.urlresolvers import reverse
from toolkit.casper.workflow_case import BaseProjectCaseMixin

from model_mommy import mommy

from .data import ENGAGELETTER_DATA as BASE_ENGAGELETTER_DATA
from ..models import EngagementLetter
from ..views import SetupEngagementLetterView


class SetupEngagementLetterViewTest(BaseProjectCaseMixin):
    """
    Specifically test the crazy uppercase lowercase domain
    """
    def setUp(self):
        super(SetupEngagementLetterViewTest, self).setUp()
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
        self.assertEqual(resp.redirect_chain, [('http://testserver/start/?next=/engagement-letters/d1c545082d1241849be039e338e47aa0/lawyer/template/', 302)])

    def test_lawyer_template_view(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.url)

        self.assertEqual(type(resp.context_data.get('view')), SetupEngagementLetterView)
        self.assertEqual(resp.context_data.get('form').fields.keys(), ['firm_name', 'firm_address', 'firm_logo', 'body'])
        self.assertEqual(resp.template_name, ['engageletter/setup_engageletter_form.html'])
        # test template data
        self.assertEqual(resp.context_data['form'].initial.get('body'), self.tool.template_source)
