# -*- coding: utf-8 -*-
from django.views.generic import DetailView
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

        user = authenticate(username=kwargs.get('slug'), password=kwargs.get('auth_slug'))
        if user:
            login(request, user)

        return super(ReviewRevisionView, self).dispatch(request=request, *args, **kwargs)

    def get_filter_ids(self):
        """
        If the user is in the participants they can see everything
        if they are just an invitee then they can only see their own comments
        """
        user = self.request.user

        if user in self.object.document.item.matter.participants.all():
            return []
        else:
            return [user.pk]

    def get_context_data(self, **kwargs):
        kwargs = super(ReviewRevisionView, self).get_context_data(**kwargs)

        crocodoc = CrocoDocConnectService(document_object=self.object.document,
                                          app_label='attachment',
                                          field_name='executed_file',
                                          upload_immediately=True)

        # @TODO this should ideally be set in the service on init
        # and session automatically updated
        CROCDOC_PARAMS = {
                "user": { "name": self.request.user.get_full_name(), 
                "id": self.request.user.pk
            }, 
            "sidebar": 'auto', 
            "editable": True, 
            "admin": False, 
            "downloadable": True, 
            "copyprotected": False, 
            "demo": False
        }

        view_url_kwargs = {
            'filter': self.get_filter_ids()
        }
        #
        # Set out session key based on params above
        #
        crocodoc.obj.crocodoc_service.session_key(**CROCDOC_PARAMS),

        kwargs.update({
            'crocodoc': crocodoc.obj.crocodoc_service,
            'crocodoc_view_url': crocodoc.obj.crocodoc_service.view_url(**view_url_kwargs),
            'CROCDOC_PARAMS': CROCDOC_PARAMS, # for testing the values
        })

        return kwargs