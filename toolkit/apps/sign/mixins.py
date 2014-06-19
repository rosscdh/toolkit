# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.storage import default_storage


# NB! hellosign is not the same lib as hello_sign
from hellosign import (HelloSignEmbeddedDocumentSignature,
                       HelloSignUnclaimedDraftDocumentSignature)
# django wrapper hello_sign imports
from hello_sign.models import HelloSignRequest
from hello_sign.services import HelloSignService

import urlparse


class HelloSignOverridesMixin(object):
    hs_request_object = None
    hs_request_object_is_new = None

    def __init__(self, *args, **kwargs):
        self.hs_request_object = None
        self.hs_request_object_is_new = None
        super(HelloSignOverridesMixin, self).__init__(*args, **kwargs)

    @property
    def hs_claim_setup_complete(self):
        """
        Does the HelloSignRequest have the hs_claim_setup_complete i.e. has the
        lawyer completed the setup stage of this form
        """
        hs_request_object = self.get_hs_request_object()
        return hs_request_object.data.get('hs_claim_setup_complete', False)  # True if we have no guid yet

    def get_hs_request_object(self, **kwargs):
        """
        Get the hs_request object based on the kwargs
        """
        self.hs_request_object, self.hs_request_object_is_new = HelloSignRequest.objects.get_or_create(content_object_type=self.get_content_type_object(),
                                                                                                       object_id=self.pk)
        return self.hs_request_object

    def get_hs_service(self, **kwargs):
        """
        OVERRIDDEN to return the HelloSignUnclaimedDraftDocumentSignature as default
        Can handle the various types of requests UnclaimedDoc as well as the standard
        """
        hs_service_kwargs = {
            'document': self.hs_document(),
            'title': self.hs_document_title(),
            'invitees': self.hs_signers(),
            'subject': self.hs_subject(),
            'message': self.hs_message()
        }
        kwargs.update(hs_service_kwargs)
        return HelloSignService(**kwargs)

    def hs_record_result(self, result):
        """
        Detect if the result is a claim request result or another type
        """
        if result.get('unclaimed_draft', None) is not None:
            #
            # Is an unclaimed draft response
            #
            update_fields = []
            unclaimed_draft = result.get('unclaimed_draft')

            signature_request_id = unclaimed_draft.get('signature_request_id')
            claim_url = unclaimed_draft.get('claim_url') # get claim url so we can **manually** (wtf hellosign) extract the gui
            parsed_url = urlparse.urlparse(claim_url)
            parsed_url_query = urlparse.parse_qs(parsed_url.query)
            unclaimed_draft_guid = parsed_url_query.get('guid', [None])[0]  # its a list so get the first one as the guid

            #
            # get the object
            #
            hs_request_object = self.get_hs_request_object(signature_request_id=signature_request_id,
                                                           unclaimed_draft_guid=unclaimed_draft_guid)

            if signature_request_id:
                hs_request_object.signature_request_id = signature_request_id
                # update this field
                update_fields.append('signature_request_id')

            if unclaimed_draft_guid:
                hs_request_object.unclaimed_draft_guid = unclaimed_draft_guid
                # update this field
                update_fields.append('unclaimed_draft_guid')

            # save the result
            hs_request_object.data = result  # save the complete unclaimed_draft result data to the object
            update_fields.append('data')

            if update_fields:
                # save the field
                hs_request_object.save(update_fields=update_fields)

            return hs_request_object

        else:
            #
            # the claim has been lodged
            #
            return super(HelloSignOverridesMixin, self).hs_record_result(result=result)


    def hs_subject(self):
        return 'Signature Request for: %s' % self.document.name

    def hs_document_title(self):
        """
        Method to set the document title, displayed in the HelloSign Interface
        """
        return self.document.name

    def hs_document(self):
        """
        Return the document to be sent for signing
        Ties in with HelloSignModelMixin method
        """
        if self.ensure_file():
            return default_storage.open(self.document.executed_file)
        return None

    def hs_signers(self):
        """
        Return a list of invitees to sign
        """
        return [{'name': u.get_full_name(), 'email': u.email} for u in self.document.signers.all()]

    def create_unclaimed_draft(self, requester_email_address, **kwargs):
        hs_request_object = self.get_hs_request_object()

        if hs_request_object and hs_request_object.unclaimed_draft_guid is not None:
            return hs_request_object.data.get('unclaimed_draft', {})
        else:
            # has not been created yet
            #
            # Claim url request
            #
            kwargs.update({
                'requester_email_address': requester_email_address,  # required for this type
            })

        result = super(HelloSignOverridesMixin, self).create_unclaimed_draft(**kwargs)
        if hasattr(result, 'json'):
            return result.json()  # return the json response from the requests lib response
        return result
