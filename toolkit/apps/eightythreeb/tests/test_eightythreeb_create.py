# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

from toolkit.casper import BaseScenarios
from toolkit.apps.eightythreeb.forms import LawyerEightyThreeBForm, CustomerEightyThreeBForm
from toolkit.apps.workspace.views import CreateToolObjectView, UpdateViewToolObjectView
from toolkit.apps.eightythreeb.markers import LawyerCompleteFormMarker, LawyerInviteUserMarker, CustomerCompleteFormMarker


class LawyerCreateEightythreebTest(BaseScenarios, TestCase):
    def setUp(self):
        super(LawyerCreateEightythreebTest, self).setUp()
        self.basic_workspace()

        self.eightythreeb.status = self.eightythreeb.STATUS.lawyer_invite_customer
        self.eightythreeb.data['markers']=   {"lawyer_complete_form": {
                                                  "actor_name": "", 
                                                  "date_of": "2013-12-30T10:52:35"
                                                }}
        self.eightythreeb.save(update_fields=['status', 'data'])

        self.client.login(username=self.lawyer.username, password=self.password)


    def test_lawyer_post_save_preview(self):
        """
        Test that the preview view shown to lawyers will
        a. redirect to the Invite Customer View
        b. have the Edit form in the previous
        """
        url = reverse('workspace:tool_object_after_save_preview', kwargs={'workspace': self.eightythreeb.workspace.slug, 'tool': self.eightythreeb.workspace.tools.filter(slug=self.eightythreeb.tool_slug).first().slug, 'slug': self.eightythreeb.slug})
        resp = self.client.get(url, follow=True)
        # test general stuff
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context_data.get('object').status, self.eightythreeb.STATUS.lawyer_invite_customer)

        # ensure we have the right prev current and next markers
        markers = resp.context_data.get('object').markers

        self.assertEqual(type(markers.previous_marker), LawyerCompleteFormMarker)
        self.assertEqual(type(markers.current_marker), LawyerInviteUserMarker)
        self.assertEqual(type(markers.next_marker), CustomerCompleteFormMarker)

        # test the urls are set correctly
        self.assertEqual(resp.context_data.get('next_url'), '/workspace/lawpal-test/tool/83b-election-letters/e0c545082d1241849be039e338e47a0f/invite/client/')
        self.assertEqual(resp.context_data.get('previous_url'), markers.previous_marker.get_action_url())
        