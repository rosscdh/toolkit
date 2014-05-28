# -*- coding: utf-8 -*-
from django.core import signing
from django.http import Http404
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import DetailView
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import BaseUpdateView

from .models import SignDocument

import logging
logger = logging.getLogger('django.request')


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
        return self.object

    def get_context_data(self, **kwargs):
        signer = get_object_or_404(User, username=self.kwargs.get('username'))
        signer_url = self.object.get_signer_signing_url(signer=signer)

        if signer_url is None:
            raise Http404('Could not get signer_url')

        kwargs = super(SignRevisionView, self).get_context_data(**kwargs)
        kwargs.update({
            'sign_url': signer_url,
            'can_sign': True #self.request.user in self.object.document.signers.all(),
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
            'claim_url': mark_safe(self.object.signing_request.data.get('unclaimed_draft', {}).get('claim_url')),
            'can_claim': self.matter.lawyer == self.request.user,
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
        # @TODO make this async using run_task
        #
        self.object.send_for_signing(signature_request_id=signature_request_id)

        return super(ClaimSignRevisionView, self).post(request=request, *args, **kwargs)

