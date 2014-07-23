# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.models import ROLES

from .. import BaseEndpointTest

from model_mommy import mommy

import json


class MatterParticipantPermissionTest(BaseEndpointTest):
    """
    test workspace.manage_participants permission
    """

    @property
    def endpoint(self):
        return reverse('matter_participant', kwargs={'matter_slug': self.matter.slug})

    def setUp(self):
        super(MatterParticipantPermissionTest, self).setUp()

        self.lawyer_to_add = mommy.make('auth.User', username='New Lawyer', email='newlawyer@lawpal.com')
        self.lawyer_to_add.set_password(self.password)
        self.lawyer_to_add.save(update_fields=['password'])

        profile = self.lawyer_to_add.profile
        profile.user_class = 'lawyer'
        profile.save(update_fields=['data'])

        self.user_to_add = mommy.make('auth.User', username='New Person', email='username@example.com')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/participant')

    def test_post_new_existing_participant(self):
        """
        Test we can add users to the participants only with manage_participants
        """
        self.client.login(username=self.user.username, password=self.password)

        data = {
            'email': self.lawyer_to_add.email,
            'first_name': 'Bob',
            'last_name': 'Crockett',
            'message': 'Bob you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.colleague)
        }

        self.set_user_matter_perms(user=self.user, manage_participants=False)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.user, manage_clients=True)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.user, manage_participants=True)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_patch_participant(self):
        self.client.login(username=self.user.username, password=self.password)

        # create user to be modified after:
        data = {
            'email': self.lawyer.email,
            'permissions': {'manage_items': True, 'manage_participants': False},
            'role': ROLES.get_name_by_value(ROLES.colleague)
        }

        self.set_user_matter_perms(user=self.user, manage_participants=False)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.user, manage_clients=True)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.user, manage_participants=True)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_delete(self):
        """
        Test we can remove users to the participants
        """
        self.client.login(username=self.user.username, password=self.password)

        #
        # Create new non-existing user
        #
        data = {
            'email': 'delete-me@lawpal.com',
            'first_name': 'Delete',
            'last_name': 'User',
            'message': 'You are about to be deleted',
            'role': ROLES.get_name_by_value(ROLES.colleague)
        }

        self.set_user_matter_perms(user=self.user, manage_participants=True)
        resp = self.client.post(self.endpoint, data)
        self.assertEqual(resp.status_code, 202)  # Accepted
        #
        # Test the primary user can delete other lawyers/users
        #
        user_to_delete = self.matter.participants.get(username='delete-me')
        user_perms = user_to_delete.matter_permissions(matter=self.matter)

        self.assertEqual(user_perms.role, ROLES.colleague)
        self.assertEqual(user_perms.role_name, 'colleague')


        # append the email to the url for DELETE
        endpoint = '%s/%s' % (self.endpoint, user_to_delete.email)

        self.set_user_matter_perms(user=self.user, manage_participants=False)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.user, manage_participants=True)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 202)  # accepted

