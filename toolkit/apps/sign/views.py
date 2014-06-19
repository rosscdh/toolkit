# -*- coding: utf-8 -*-
from django.http import Http404
from django.contrib.auth.models import User
from django.views.generic import DetailView
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
from django.views.generic.edit import BaseUpdateView

from hellosign_sdk.utils.exception import Conflict

from toolkit.tasks import run_task

from .models import SignDocument
from .tasks import _send_for_signing

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

    @property
    def is_authorised(self):
        return self.request.user in self.object.document.signers.all() or self.request.user == self.object.requested_by or self.request.user == self.matter.lawyer

    def get_template_names(self):
        if self.object.is_current is False:
            return ['sign/sign-nolongercurrent.html']
        else:
            return [self.template_name]

    def get_object(self):
        self.object = super(SignRevisionView, self).get_object()
        self.matter = self.object.document.item.matter

        self.signer = None
        if self.kwargs.get('username', None) is not None:
            self.signer = get_object_or_404(User, username=self.kwargs.get('username'))

        return self.object

    def get_context_data(self, **kwargs):
        try:
            signer_url = self.object.get_signer_signing_url(signer=self.signer)

        except Conflict as e:
            #
            # The signature has already been signed
            #
            logger.error('Conflict: %s' % e)

            self.template_name = 'sign/already-signed.html'
            signer_url = False

        if signer_url is None:
            raise Http404('Could not get signer_url')

        kwargs = super(SignRevisionView, self).get_context_data(**kwargs)
        kwargs.update({
            'sign_url': signer_url,
            'signer': self.signer,
            'signed_on': self.object.signed_at(signer=self.signer),
            'can_sign': self.is_authorised,
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        resp = super(SignRevisionView, self).get(request=request, *args, **kwargs)

        # create event
        self.matter.actions.user_viewed_signature_request(user=request.user,
                                                          signer=self.signer,
                                                          sign_document=self.object)
        return resp


class ClaimSignRevisionView(SignRevisionView,
                            BaseUpdateView):

    template_name = 'sign/claim.html'
    http_method_names = [u'get', u'post']

    def get_template_names(self):
        if self.object.is_current is False:
            return ['sign/sign-nolongercurrent.html']
        else:
            return ['sign/claim.html']

    @property
    def is_authorised(self):
        return self.request.user == self.object.requested_by or self.request.user == self.matter.lawyer

    def get_context_data(self, **kwargs):
        kwargs = super(SignRevisionView, self).get_context_data(**kwargs)  # NB! we call SignRevisionView so we dont get the user checking that takes place in SignRevisionView
        kwargs.update({
            'claim_url': mark_safe(self.object.signing_request.data.get('unclaimed_draft', {}).get('claim_url')),
            'can_claim': self.is_authorised,
            'requested_by': self.object.requested_by
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        resp = super(ClaimSignRevisionView, self).get(request=request, *args, **kwargs)

        # send log event
        self.matter.actions.sent_setup_for_signing(user=request.user, sign_object=self.object)

        return resp

    def post(self, request, *args, **kwargs):
        """
        Handle the claim_url postback when the user has completed the claim setup
        """
        signature_request_id = request.POST.get('signature_request_id')
        subject = request.POST.get('subject', None)  # HS to rpovide these, currently missing
        message = request.POST.get('message', None)  # HS to rpovide these, currently missing

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
        # Perform the document send for signing and the email process async
        #
        run_task(_send_for_signing,
                 from_user=request.user,
                 sign_object=self.object,
                 signature_request_id=signature_request_id,
                 subject=subject,
                 message=message)

        # send log event
        self.matter.actions.completed_setup_for_signing(user=request.user, sign_object=self.object)

        return super(ClaimSignRevisionView, self).post(request=request, *args, **kwargs)
