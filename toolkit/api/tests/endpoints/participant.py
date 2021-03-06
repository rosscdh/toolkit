# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.reverse import reverse

from django.dispatch import receiver

from toolkit.apps.matter.signals import PARTICIPANT_ADDED
from toolkit.apps.workspace.models import Workspace, ROLES

from . import BaseEndpointTest

from model_mommy import mommy

import json


class MatterParticipantTest(BaseEndpointTest):
    """
    Test that the matter can have participants added and removed

    POST /matters/:matter_slug/participant
    {
        "email": "username@example.com"
    }
    DELETE /matters/:matter_slug/participant/username@example.com

    @RULE Can not delete the participant if it is the same as matter.lawyer
    @RULE Can not delete a participant if it is the same as the matter.client.primary @TODO this is a discussion point
    """

    @property
    def endpoint(self):
        return reverse('matter_participant', kwargs={'matter_slug': self.matter.slug})

    def setUp(self):
        super(MatterParticipantTest, self).setUp()

        self.lawyer_to_add = mommy.make('auth.User', username='New Lawyer', email='newlawyer@lawpal.com')
        self.lawyer_to_add.set_password(self.password)
        self.lawyer_to_add.save(update_fields=['password'])

        self.matter.add_participant(user=self.lawyer_to_add, role=ROLES.colleague)

        profile = self.lawyer_to_add.profile
        profile.user_class = 'lawyer'
        profile.save(update_fields=['data'])

        self.user_to_add = mommy.make('auth.User', first_name='Gorilla', last_name='Boots', username='New Person',
                                      email='username@example.com')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/participant')

    def test_lawyer_get(self):
        """
        No get on this endpoint as its only allows update
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_post_existing_user(self):
        """
        Test we can add users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        @receiver(PARTICIPANT_ADDED)
        def f(matter, participant, user, **kwargs):
            self.signal_called = True

        new_lawyer_to_add = mommy.make('auth.User', first_name='Bob', last_name='Crockett',
                                       username='another-new-lawyer', email='anothernewlawyer@lawpal.com')

        #
        # Add the new Lawyer (Signal gets called)
        #
        data = {
            'email': new_lawyer_to_add.email,
            'first_name': new_lawyer_to_add.first_name,
            'last_name': new_lawyer_to_add.last_name,
            'message': 'Bob you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.colleague),
        }

        self.signal_called = False
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 202)  # accepted
        self.assertTrue(self.signal_called)

        #
        # Try to re-add the lawyer (Signal doesn't get called)
        #
        data = {
            'email': self.lawyer_to_add.email,
            'first_name': 'Bob',
            'last_name': 'Crockett',
            'message': 'Bob you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.colleague),
        }

        self.signal_called = False
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 304)  # not modified
        self.assertFalse(self.signal_called)

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)
        participants = self.matter.participants.all()
        self.assertEqual(len(participants), 4)  # we have 3 users and a matter owner (lawyer)
        self.assertTrue(self.lawyer in participants)

        #
        # Add the New User (Signal gets called)
        #
        data = {
            'email': self.user_to_add.email,
            'first_name': self.user_to_add.first_name,
            'last_name': self.user_to_add.last_name,
            'message': 'Boots you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.thirdparty),
        }

        self.signal_called = False
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted
        self.assertTrue(self.signal_called)

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)
        participants = self.matter.participants.all()
        self.assertEqual(len(participants), 5)  # we have 4 users and a matter owner (lawyer)
        self.assertTrue(self.user_to_add in participants)

    def test_lawyer_post_new_user_who_does_not_yet_exist(self):
        """
        Can add a user from just the email
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Add the New Lawyer
        #
        data = {
            'email': 'test+monkey@lawyer.com',
            'first_name': 'Test',
            'last_name': 'Monkey',
            'message': 'Test Monkey you are being added here please do something',
            'role': ROLES.get_name_by_value(ROLES.thirdparty),
        }

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

        new_user = User.objects.get(email=data.get('email'))

        self.assertTrue(new_user)  # exists
        self.assertEqual(new_user.first_name, 'Test')
        self.assertEqual(new_user.last_name, 'Monkey')
        self.assertTrue(new_user.profile.is_customer)
        # we patch the get_full_name object to return email if first_name and last_name are nothing
        self.assertEqual(new_user.get_full_name(), 'Test Monkey')

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'username': self.lawyer_to_add.username,
            'permissions': {'manage_items': True, 'manage_participants': False},
            'role': ROLES.get_name_by_value(ROLES.colleague)
        }

        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

        user = User.objects.get(username=data['username'])
        self.assertTrue(user.has_perm('workspace.manage_items', self.matter))
        self.assertFalse(user.has_perm('workspace.manage_participants', self.matter))

    def test_lawyer_delete(self):
        """
        Test we can remove users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Test the primary lawyer can delete other lawyers/users
        #
        user_to_delete = self.matter.participants.get(username='test-customer')
        # append the email to the url for DELETE
        endpoint = '%s/%s' % (self.endpoint, user_to_delete.username)

        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 202)  # accepted

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        participants = self.matter.participants.all()

        self.assertEqual(len(participants), 2)  # we have 1 users (the additional lawyer user ) and the primary matter owner
        self.assertTrue(self.lawyer in participants)
        self.assertTrue(self.lawyer_to_add in participants)

    def test_lawyer_cant_delete_main_lawyer(self):
        """
        Prevent another lawyer that has been added from deleteing the main lawyer
        from the participants
        """
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        self.assertEqual(len(self.matter.participants.all()), 3)

        # login as the new lawyer guy
        self.client.login(username=self.lawyer_to_add.username, password=self.password)

        #
        # Test the primary lawyer cant be removed
        #
        user_to_delete = self.lawyer

        endpoint = '%s/%s' % (self.endpoint, user_to_delete.username)

        resp = self.client.delete(endpoint, None)

        self.assertEqual(resp.status_code, 403)  # forbidden

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        participants = self.matter.participants.all()
        self.assertEqual(len(participants), 3)  # we have 0 users and a matter owner (lawyer)
        # make sure he is still in there
        self.assertTrue(self.matter.lawyer in participants)

    def test_customer_cant(self):
        self.client.login(username=self.user.username, password=self.password)

        user_to_delete = self.matter.participants.all().last()

        self.set_user_matter_perms(self.user, matter=self.matter, manage_participants=False, manage_clients=False)
        self.set_user_matter_role(self.user, role=ROLES.client, matter=self.matter)

        for event, status_code in [('get', 405), ('post', 403), ('patch', 403), ('delete', 403)]:
            endpoint = '%s/%s' % (self.endpoint, user_to_delete.username) if event == 'delete' else self.endpoint
            resp = getattr(self.client, event)(endpoint, {}, content_type='application/json')
            self.assertEqual(resp.status_code, status_code)

    def test_anon_cant(self):
        for event in ['get', 'post', 'patch', 'delete']:
            resp = getattr(self.client, event)(self.endpoint, {}, content_type='application/json')
            self.assertEqual(resp.status_code, 403)  # forbidden
