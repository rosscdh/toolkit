# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout

from dj_crocodoc.services import CrocoDocConnectService

from .models import ReviewDocument


class ReviewRevisionView(DetailView):
    """
    View to allow an authenticated user to view a crocodoc url that is connected
    to a core.attachment revision
    """
    queryset = ReviewDocument.objects.prefetch_related().all()
    template_name = 'review/review.html'

    def dispatch(self, request, *args, **kwargs):
        return super(ReviewRevisionView, self).dispatch(request=request, *args, **kwargs)

    def can_read(self):
        #
        # Log in using the review backend
        # 'toolkit.apps.review.auth_backends.ReviewDocumentBackend'
        #
        requested_authenticated_user = authenticate(username=self.kwargs.get('slug'), password=self.kwargs.get('auth_slug'))

        if self.request.user.is_authenticated() is True:
            #
            # if the request user is in the object.participants
            # it means they are owners and should be able to view this regardless
            #
            if self.request.user in self.matter.participants.all():
                # we are an owner its all allowed
                pass
            else:
                #
                # user is we are already logged in then check this guys mojo!
                #
                if requested_authenticated_user != self.request.user:
                    raise PermissionDenied

                if user:
                    login(self.request, user)

    def get_object(self):
        obj = super(ReviewRevisionView, self).get_object()
        self.matter = obj.document.item.matter

        self.can_read()

        return obj

    def get_context_data(self, **kwargs):
        kwargs = super(ReviewRevisionView, self).get_context_data(**kwargs)

        crocodoc = CrocoDocConnectService(document_object=self.object.document,
                                          app_label='attachment',
                                          field_name='executed_file',
                                          upload_immediately=True)

        # @TODO this should ideally be set in the service on init
        # and session automatically updated
        # https://crocodoc.com/docs/api/ for more info
        CROCDOC_PARAMS = {
                "user": { "name": self.request.user.get_full_name(), 
                "id": self.request.user.pk
            }, 
            "sidebar": 'auto',
            "editable": True, # allow comments
            "admin": False, # noone should be able to delete other comments
            "downloadable": True, # everyone should be able to download a copy
            "copyprotected": False, # should not have copyprotection
            "demo": False,
            #
            # We create a ReviewDocument object for each and every reviewer
            # for the matter.participants there is 1 ReviewDocument object
            # that they all can see
            #
            #"filter": self.get_filter_ids() # must be a comma seperated list
        }
        #
        # Set out session key based on params above
        #
        crocodoc.obj.crocodoc_service.session_key(**CROCDOC_PARAMS),

        kwargs.update({
            'crocodoc': crocodoc.obj.crocodoc_service,
            'crocodoc_view_url': crocodoc.obj.crocodoc_service.view_url(**CROCDOC_PARAMS),  # this is where the view params must be sent in order to show toolbar etc
            'CROCDOC_PARAMS': CROCDOC_PARAMS, # for testing the values
        })

        return kwargs