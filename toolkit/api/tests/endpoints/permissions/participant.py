# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.dispatch import receiver

from toolkit.apps.matter.services.matter_permission import MightyMatterUserPermissionService
from toolkit.apps.matter.signals import PARTICIPANT_ADDED
from toolkit.apps.workspace.models import Workspace, ROLES

from . import BaseEndpointTest

from model_mommy import mommy

import json


class MatterParticipantTest(BaseEndpointTest):
    """
    test workspace.manage_participants permission
    """

    @property
    def endpoint(self):
        return reverse('matter_participant', kwargs={'matter_slug': self.matter.slug})

    def setUp(self):
        super(MatterParticipantTest, self).setUp()

        self.lawyer_to_add = mommy.make('auth.User', username='New Lawyer', email='newlawyer@lawpal.com')
        self.lawyer_to_add.set_password(self.password)
        self.lawyer_to_add.save(update_fields=['password'])

        profile = self.lawyer_to_add.profile
        profile.user_class = 'lawyer'
        profile.save(update_fields=['data'])

        self.user_to_add = mommy.make('auth.User', username='New Person', email='username@example.com')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/participant')

    def test_lawyer_post_existing_user(self):
        """
        Test we can add users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'email': self.lawyer_to_add.email,
            'first_name': 'Bob',
            'last_name': 'Crockett',
            'message': 'Bob you are being added here please do something',
        }

        self.set_user_permissions(self.lawyer, {'workspace.manage_participants': False})
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_permissions(self.lawyer, {'workspace.manage_participants': True})
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # create user to be modified after:
        user = mommy.make('auth.User', email='test+monkey@lawyer.com')
        MightyMatterUserPermissionService(matter=self.matter,
                                          role=ROLES.customer,
                                          user=user,
                                          changing_user=user).process()
        data = {
            'email': 'test+monkey@lawyer.com',
            'permissions': {'workspace.manage_items': True, 'workspace.manage_participants': False},
            'role': ROLES.lawyer
        }

        self.set_user_permissions(self.lawyer, {'workspace.manage_participants': False})
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_permissions(self.lawyer, {'workspace.manage_participants': True})
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_lawyer_delete(self):
        """
        Test we can remove users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Test the primary lawyer can delete other lawyers/users
        #
        user_to_delete = self.matter.participants.all().first()
        # append the email to the url for DELETE
        endpoint = '%s/%s' % (self.endpoint, user_to_delete.email)

        self.set_user_permissions(self.lawyer, {'workspace.manage_participants': False})
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 403)  # accepted

        self.set_user_permissions(self.lawyer, {'workspace.manage_participants': True})
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 202)  # accepted