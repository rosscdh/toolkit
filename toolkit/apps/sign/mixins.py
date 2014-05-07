# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.storage import default_storage


# NB! hellosign is not the same lib as hello_sign
from hellosign import HelloSignUnclaimedDraftDocumentSignature
# django wrapper hello_sign imports
from hello_sign.models import HelloSignRequest
from hello_sign.services import HelloSignService

import urlparse


class HelloSignOverridesMixin(object):
    def get_hs_service(self):
        """
        OVERRIDDEN to return the HelloSignUnclaimedDraftDocumentSignature as default
        """
        return HelloSignService(HelloSignSignatureClass=HelloSignUnclaimedDraftDocumentSignature,  # Passed in to override the default
                                document=self.hs_document(),
                                title=self.hs_document_title(),
                                invitees=self.hs_signers(),
                                subject=self.hs_subject(),
                                message=self.hs_message())

    def hs_post_process_result(self, resp):
        result = resp.json()
        #
        # Clean ugly HS namespace
        #
        result = result.get('unclaimed_draft', result)

        if 'claim_url' in result:
            # append client_id to the claim_url attrib
            result['claim_url_with_client_id'] = '%s&client_id=%s' % (result['claim_url'], settings.HELLOSIGN_CLIENT_ID)

        return result

    def hs_record_result(self, result):
        """
        Because HS's api is so crap they dont give us an identifying GUID as part
        of the standard json, instead we have to manually parse the gui out of their crappy
        claim_url response, wasting precious cycles
        """
        claim_url = result.get('claim_url') # get claim url so we can **manually** (wtf hellosign) extract the gui
        parsed_url = urlparse.urlparse(claim_url)
        parsed_url_query = urlparse.parse_qs(parsed_url.query)
        unclaimed_draft_guid = parsed_url_query.get('guid')

        if unclaimed_draft_guid:
            if type(unclaimed_draft_guid) in [list]:
                unclaimed_draft_guid = unclaimed_draft_guid[0]  # its a list so get the first one as the guid

            hs_request_object, is_new = HelloSignRequest.objects.get_or_create(unclaimed_draft_guid=unclaimed_draft_guid,
                                                                               content_object_type=self.get_content_type_object(),
                                                                               object_id=self.pk)
            # save the result
            hs_request_object.data = result
            # save the field
            hs_request_object.save(update_fields=['data'])

            return hs_request_object
        return None


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
        return default_storage.open(self.document.executed_file)

    def hs_signers(self):
        """
        Return a list of invitees to sign
        """
        return [{'name': u.get_full_name(), 'email': u.email} for u in self.signers.all()]
