# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout

from dj_crocodoc.services import CrocoDocConnectService

from .models import SignDocument


class SignRevisionView(DetailView):
    """
    View to allow an authenticated user to view a crocodoc url that is connected
    to a core.attachment revision
    """
    queryset = SignDocument.objects.prefetch_related().all()
    template_name = 'sign/sign.html'

    def dispatch(self, request, *args, **kwargs):
        #
        # Log in using the sign backend
        # 'toolkit.apps.sign.auth_backends.SignDocumentBackend'
        #
        user = authenticate(username=kwargs.get('slug'), password=kwargs.get('auth_slug'))

        if request.user.is_authenticated() is True:
            #
            # user is we are already logged in then check this guys mojo!
            #
            if request.user != user:
                raise PermissionDenied

        if user:
            login(request, user)

        return super(SignRevisionView, self).dispatch(request=request, *args, **kwargs)

    def get_filter_ids(self):
        """
        If the user is in the participants they can see everything
        if they are just an invitee then they can only see their own comments
        """
        user = self.request.user
        matter = self.object.document.item.matter
        if user in matter.participants.all():
            return None
        else:
            return ','.join([str(user.pk), str(user.pk)])

    def get_context_data(self, **kwargs):
        kwargs = super(SignRevisionView, self).get_context_data(**kwargs)
        
        # test the file is present locally
        if self.object.file_exists_locally is False:
            # its not so download it locally so we can send the file to crocodoc
            # and not deal with s3 permissions
            self.object.download_if_not_exists()

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
            # We create a SignDocument object for each and every signer
            # for the matter.participants there is 1 SignDocument object
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
