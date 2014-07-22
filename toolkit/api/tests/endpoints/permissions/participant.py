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

    def test_lawyer_post_existing_user(self):
        """
        Test we can add users to the participants only with manage_participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'email': self.lawyer_to_add.email,
            'first_name': 'Bob',
            'last_name': 'Crockett',
            'message': 'Bob you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.colleague)
        }

        self.set_user_matter_perms(user=self.lawyer, manage_participants=False)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_clients=True)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_participants=True)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_lawyer_post_existing_client(self):
        """
        Test we can add client with permission manage_clients
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'email': self.lawyer_to_add.email,
            'first_name': 'Bob',
            'last_name': 'Crockett',
            'message': 'Bob you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.client)
        }

        self.set_user_matter_perms(user=self.lawyer, manage_clients=False)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_clients=True)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_lawyer_post_existing_client_with_participants_perm(self):
        """
        Test we can add client with manage_participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'email': self.lawyer_to_add.email,
            'first_name': 'Bob',
            'last_name': 'Crockett',
            'message': 'Bob you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.client)
        }

        self.set_user_matter_perms(user=self.lawyer, manage_participants=False)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_participants=True)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted because client is included in participants

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # create user to be modified after:
        data = {
            'email': self.lawyer.email,
            'permissions': {'manage_items': True, 'manage_participants': False},
            'role': ROLES.get_name_by_value(ROLES.colleague)
        }

        self.set_user_matter_perms(user=self.lawyer, manage_participants=False)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_clients=True)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_participants=True)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

    # def test_lawyer_patch_client(self):
    #     self.client.login(username=self.lawyer.username, password=self.password)

    #     # create user to be modified after:
    #     data = {
    #         'email': self.lawyer.email,
    #         'permissions': {'manage_items': True, 'manage_participants': False},
    #         'role': ROLES.get_name_by_value(ROLES.client)
    #     }

    #     self.set_user_matter_perms(user=self.lawyer, manage_clients=False)
    #     resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
    #     self.assertEqual(resp.status_code, 403)  # forbidden

    #     self.set_user_matter_perms(user=self.lawyer, manage_clients=True)
    #     resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
    #     self.assertEqual(resp.status_code, 202)  # accepted

    def test_lawyer_patch_client_with_participants_perm(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # create user to be modified after:
        data = {
            'email': self.lawyer.email,
            'permissions': {'manage_items': True, 'manage_participants': False},
            'role': ROLES.get_name_by_value(ROLES.client)
        }

        self.set_user_matter_perms(user=self.lawyer, manage_participants=False)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_participants=True)
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
        user_perms = user_to_delete.matter_permissions(matter=self.matter)
        user_perms.role = ROLES.colleague
        user_perms.save(update_fields=['role'])

        # append the email to the url for DELETE
        endpoint = '%s/%s' % (self.endpoint, user_to_delete.email)

        self.set_user_matter_perms(user=self.lawyer, manage_participants=False)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 403)  # forbidden

        # self.set_user_matter_perms(user=self.lawyer, manage_clients=True)
        # resp = self.client.delete(endpoint, None)
        # self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_participants=True)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_lawyer_delete_client(self):
        """
        Test we can remove users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Test the primary lawyer can delete other lawyers/users
        #
        user_to_delete = self.matter.participants.all().first()
        self.set_user_matter_role(user_to_delete, ROLES.client, self.matter)

        # append the email to the url for DELETE
        endpoint = '%s/%s' % (self.endpoint, user_to_delete.email)

        self.set_user_matter_perms(user=self.lawyer, manage_clients=False)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 403)  # forbidden

        # self.skipTest('we need to make sure if manage_clients includes to remove participants with role "client" from the matter')

        self.set_user_matter_perms(user=self.lawyer, manage_clients=True)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 202)  # accepted

    def test_lawyer_delete_client_with_participants_perm(self):
        """
        Test we can remove users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Test the primary lawyer can delete other lawyers/users
        #
        user_to_delete = self.matter.participants.all().first()
        self.set_user_matter_role(user_to_delete, ROLES.client, self.matter)

        # append the email to the url for DELETE
        endpoint = '%s/%s' % (self.endpoint, user_to_delete.email)

        self.set_user_matter_perms(user=self.lawyer, manage_participants=False)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_participants=True)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 202)  # accepted