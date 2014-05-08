# -*- coding: utf-8 -*-
from django.http import Http404
from django.views.generic import DetailView
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from django.views.generic.edit import BaseUpdateView

from .models import SignDocument

import logging
logger = logging.getLogger('django.request')


def _authenticate(request, obj, matter, **kwargs):
    #
    # Log in using the review backend
    # 'toolkit.apps.review.auth_backends.ReviewDocumentBackend'
    #
    requested_authenticated_user = authenticate(username=kwargs.get('slug'), password=kwargs.get('auth_slug'))

    if requested_authenticated_user:
        #
        # if the request user is in the object.participants
        # it means they are owners and should be able to view this regardless
        #
        if request.user in matter.participants.all():
            #
            # we are an owner its all allowed
            #
            pass
        else:
            #
            # user is we are already logged in then check this guys mojo!
            #
            if request.user.is_authenticated():
                if requested_authenticated_user != request.user:
                    raise PermissionDenied

            #
            # We are indeed the reviewer and are reviewing the document
            #
            login(request, requested_authenticated_user)
            # only for the reviewer, we dont do this for when participants view
            obj.signer_has_viewed = True


class SignRevisionView(DetailView):
    """
    View to allow an authenticated user to view a crocodoc url that is connected
    to a core.attachment revision
    """
    queryset = SignDocument.objects.prefetch_related().all()
    template_name = 'sign/sign.html'

    @property
    def user_is_matter_participant(self):
        """
        Test the current user is part of the high level matter.participants who
        can view any and al previous revisions
        """
        return self.request.user in self.matter.participants.all()

    def get_template_names(self):
        if self.object.is_current is False:
            return ['sign/sign-nolongercurrent.html']
        else:
            return ['sign/sign.html']

    def get_object(self):
        self.object = super(SignRevisionView, self).get_object()
        self.matter = self.object.document.item.matter

        #
        # Perform authentication of the user here
        # not required for signing
        # _authenticate(request=self.request, obj=self.object, matter=self.matter, **self.kwargs)

        return self.object

    def get_context_data(self, **kwargs):
        kwargs = super(SignRevisionView, self).get_context_data(**kwargs)
        import pdb;pdb.set_trace()
        kwargs.update({
            'sign_url': mark_safe(self.object.signing_request.get_absolute_url())
        })
        return kwargs


class ClaimSignRevisionView(SignRevisionView,
                            BaseUpdateView):

    template_name = 'sign/claim.html'
    http_method_names = [u'get', u'post']

    def get_template_names(self):
        if self.object.is_current is False:
            return ['sign/sign-nolongercurrent.html']
        else:
            return ['sign/claim.html']

    def get_context_data(self, **kwargs):
        kwargs = super(SignRevisionView, self).get_context_data(**kwargs)
        kwargs.update({
            'claim_url': mark_safe(self.object.signing_request.data.get('unclaimed_draft', {}).get('claim_url'))
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        Handle the claim_url postback when the user has completed the claim setup
        """
        signature_request_id = request.POST.get('signature_request_id')
        logger.info('found signature_request_id: %s' % signature_request_id)

        self.object = self.get_object()
        object_signature_request = self.object.signing_request  # Get the HelloSignReqeust object for this SignDocument

        if not object_signature_request or object_signature_request.signature_request_id != signature_request_id:
            logger.error('signature_request_id did not match for %s self.object.signing_request: %s != %s' % (self.object.signing_request, self.object.signing_request.signature_request_id, signature_request_id))
            raise Http404

        # set the is_claimed property
        object_signature_request.data['is_claimed'] = True
        object_signature_request.save(update_fields=['data'])
        #
        # Ok we have it all, now we can send it for signing
        #
        self.object.send_for_signing(signature_request_id=signature_request_id)

        return super(ClaimSignRevisionView, self).post(request=request, *args, **kwargs)

