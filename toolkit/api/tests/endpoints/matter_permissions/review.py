# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse

from toolkit.casper.workflow_case import PyQueryMixin

from .. import BaseEndpointTest

from model_mommy import mommy

import json


class RevisionReviewsPermissionTest(PyQueryMixin, BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewers/ (GET,POST)
        [lawyer,customer] to list, create reviewers
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'username', u'user_review', u'url', u'initials', u'user_class', u'name',
                                           u'role']

    @property
    def endpoint(self):
        return reverse('item_revision_reviewers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/reviewers' %
                         (self.matter.slug, self.item.slug))

    def setUp(self):
        super(RevisionReviewsPermissionTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')
        data = {
            "username": participant.username
        }

        self.set_user_matter_perms(user=self.lawyer, manage_document_reviews=False)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_document_reviews=True)
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created