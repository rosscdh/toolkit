# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.models import Workspace

from . import BaseEndpointTest
from ...serializers import ClientSerializer

from model_mommy import mommy

import json
import random



class MatterParticipantTest(BaseEndpointTest):
    """
    Test that the matter can have participants added and removed

    POST /matters/:matter_slug/participant
    {
        "email": "username@example.com"
    }
    DELETE /matters/:matter_slug/participant/:email_address

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

        profile = self.lawyer_to_add.profile
        profile.user_class = 'lawyer'
        profile.save(update_fields=['data'])

        self.user_to_add = mommy.make('auth.User', username='New Person', email='username@example.com')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/participant')

    def test_lawyer_get(self):
        """
        No get on this endpoint as its only allows update
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_post(self):
        """
        Test we can add users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Add the New Lawyer
        #
        data = {'email': self.lawyer_to_add.email}

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)
        participants = self.matter.participants.all()
        self.assertEqual(len(participants), 3)  # we have 2 users and a lawyer
        self.assertTrue(self.lawyer in participants)

        #
        # Add the New User
        #
        data = {'email': self.user_to_add.email}

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)
        participants = self.matter.participants.all()
        self.assertEqual(len(participants), 4)  # we have 3 users and a lawyer
        self.assertTrue(self.user_to_add in participants)


    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')

        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_delete(self):
        """
        Test we can remove users to the participants
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Test the primary lawyer can delete other lawyers/users
        #
        user_to_delete = self.matter.participants.all().first()
        data = {'email': user_to_delete.email}

        resp = self.client.delete(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 202)  # accepted

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        participants = self.matter.participants.all()
        self.assertEqual(len(participants), 1)  # we have 0 users and a lawyer
        self.assertTrue(self.lawyer in participants)

    def test_lawyer_cant_delete_main_lawyer(self):
        """
        Prevent another lawyer that has been added from deleteing the main lawyer
        from the participants
        """
        # add new layer to participants
        self.matter.participants.add(self.lawyer_to_add)
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        self.assertEqual(len(self.matter.participants.all()), 3)

        # login as the new lawyer guy
        self.client.login(username=self.lawyer_to_add.username, password=self.password)

        #
        # Test the primary lawyer cant be removed
        #
        user_to_delete = self.lawyer
        data = {'email': user_to_delete.email}

        resp = self.client.delete(self.endpoint, json.dumps(data), content_type='application/json')
        
        self.assertEqual(resp.status_code, 403)  # forbidden

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        participants = self.matter.participants.all()
        self.assertEqual(len(participants), 3)  # we have 0 users and a lawyer
        # make sure he is still in there
        self.assertTrue(self.matter.lawyer in participants)

    def test_customer_cant(self):
        self.client.login(username=self.user.username, password=self.password)
        for event, status_code in [('get', 405), ('post', 403), ('patch', 403), ('delete', 403)]:
            resp = getattr(self.client, event)(self.endpoint, {}, content_type='application/json')
            self.assertEqual(resp.status_code, status_code)

    def test_anon_cant(self):
        for event in ['get', 'post', 'patch', 'delete']:
            resp = getattr(self.client, event)(self.endpoint, {}, content_type='application/json')
            self.assertEqual(resp.status_code, 401)  # denied
