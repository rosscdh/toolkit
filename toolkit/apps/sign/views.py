# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login


from .models import SignDocument


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
        kwargs.update({
            'sign_url': self.object.signing_request.get_absolute_url()
        })
        return kwargs


class ClaimSignRevisionView(SignRevisionView):
    template_name = 'sign/claim.html'

    def get_template_names(self):
        if self.object.is_current is False:
            return ['sign/sign-nolongercurrent.html']
        else:
            return ['sign/claim.html']

    def get_context_data(self, **kwargs):
        kwargs = super(SignRevisionView, self).get_context_data(**kwargs)
        kwargs.update({
            'claim_url': self.object.signing_request.data.get('claim_url')
        })
        return kwargs
