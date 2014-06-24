# -*- coding: utf-8 -*-
from django.core import mail
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from django.core.validators import URLValidator

from toolkit.casper.workflow_case import PyQueryMixin
from toolkit.casper.prettify import mock_http_requests

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from toolkit.apps.sign.models import SignDocument
from toolkit.apps.workspace.models import InviteKey

from .. import BaseEndpointTest

from model_mommy import mommy
from rest_framework.reverse import reverse

import os
import json
import urllib

TEST_PDF_PATH = os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf')


class RevisionSignaturesPermissionTest(PyQueryMixin, BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/signers/ (GET,POST)
        [lawyer,customer] to list, create signers
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'username', u'user_review', u'url', u'initials', u'user_class', u'name',
                                           u'role']

    @property
    def endpoint(self):
        return reverse('item_revision_signers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(RevisionSignaturesPermissionTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        with open(TEST_PDF_PATH) as executed_file:
            self.revision = mommy.make('attachment.Revision',
                                        executed_file=File(executed_file),
                                        slug=None,
                                        item=self.item,
                                        uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/signers' % (self.matter.slug,
                                                                                          self.item.slug))

    def test_lawyer_post(self):
        """
        This is a bit of an anti pattern
        we POST a username into the endpoint
        and the system will create an account as well as assign them as a signer
        to the item revision
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1',
                                 email='participant+1@lawpal.com')
        dict_to_request = {'signers': [{
            'email': participant.email,
            'first_name': participant.first_name,
            'last_name': participant.last_name,
            'message': 'There should only be 1 created in total for this person',
        }]}

        self.set_user_matter_perms(user=self.lawyer, manage_signature_requests=False)
        resp = self.add_signers(data=dict_to_request)
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_signature_requests=True)
        resp = self.add_signers(data=dict_to_request)
        self.assertEqual(resp.status_code, 201)  # created


class RevisionSignerPermissionTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/signer/:username (GET,DELETE)
        [lawyer,customer] to view, delete signers
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'username', u'user_review', u'url', u'initials', u'user_class', u'name',
                                           u'role']

    @property
    def endpoint(self):
        return reverse('item_revision_signer', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug, 'username': self.participant.username})

    def setUp(self):
        super(RevisionSignerPermissionTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision',
                                   executed_file=None,
                                   slug=None,
                                   item=self.item,
                                   uploaded_by=self.lawyer)

        with open(os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf'), 'r') as filename:
            self.revision.executed_file.save('test.pdf', File(filename))
            self.revision.save(update_fields=['executed_file'])

        self.participant = mommy.make('auth.User', username='authorised-signer', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')
        self.participant.set_password(self.password)
        #
        # NB! by using the signdocument.signals and attachment.signals we are able to ensure that
        # all revision.signers are added to the appropriate signdocument objects
        # which means they can get an auth url to review the document
        #
        self.revision.signers.add(self.participant)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint,
                         '/api/v1/matters/%s/items/%s/revision/signer/%s' % (self.matter.slug,
                                                                             self.item.slug,
                                                                             self.participant.username))

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        self.set_user_matter_perms(user=self.lawyer, manage_signature_requests=False)
        resp = self.client.delete(self.endpoint)
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_signature_requests=True)
        resp = self.client.delete(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # ok
