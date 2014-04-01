# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from dj_crocodoc.services import CrocoDocConnectService

from .models import ReviewDocument

import os


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
            obj.reviewer_has_viewed = True


class ReviewRevisionView(DetailView):
    """
    View to allow an authenticated user to view a crocodoc url that is connected
    to a core.attachment revision
    """
    queryset = ReviewDocument.objects.prefetch_related().all()
    template_name = 'review/review.html'

    @property
    def user_is_matter_participant(self):
        """
        Test the current user is part of the high level matter.participants who
        can view any and al previous revisions
        """
        return self.request.user in self.matter.participants.all()

    def get_template_names(self):
        if self.object.is_current is False and self.user_is_matter_participant is False:
            return ['review/review-nolongercurrent.html']
        else:
            return ['review/review.html']

    def get_object(self):
        self.object = super(ReviewRevisionView, self).get_object()
        self.matter = self.object.document.item.matter
        #
        # Perform authentication of the user here
        #
        _authenticate(request=self.request, obj=self.object, matter=self.matter, **self.kwargs)

        return self.object

    def get_context_data(self, **kwargs):
        kwargs = super(ReviewRevisionView, self).get_context_data(**kwargs)

        crocodoc = CrocoDocConnectService(document_object=self.object.document,
                                          app_label='attachment',
                                          field_name='executed_file',
                                          upload_immediately=True,
                                          # important for sandboxing the view to ths reviewer
                                          reviewer=self.object.reviewer)
        #
        # ok this is a brand new file, we now need to ensure its available lcoally
        # and then if/when it is upload it to crocdoc
        #
        # if crocodoc.is_new is True:
        #     #
        #     # Ensure we have a local copy of this file so it can be sent
        #     #
        #     if self.object.ensure_file():
        #         # so we have a file, now lets upload it
        #         crocodoc.generate()

        # @TODO this should ideally be set in the service on init
        # and session automatically updated
        # https://crocodoc.com/docs/api/ for more info
        CROCDOC_PARAMS = {
                "user": {
                    "name": self.request.user.get_full_name(),
                    "id": self.request.user.pk
                },
                "sidebar": 'auto',
                "editable": self.object.is_current, # allow comments only if the item is current
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
            'CROCDOC_PARAMS': CROCDOC_PARAMS,  # for testing the values
        })

        return kwargs


class DownloadRevision(ReviewRevisionView):
    """
    Class to allow a matter.participant to download a copy of the file
    without exposing the s3 url to anyone
    """
    def get_context_data(self, **kwargs):
        # REMEMBER not to call super here as we dont want crocdoc near this
        self.object.ensure_file()

    def render_to_response(self, context, **response_kwargs):
        #
        # Use our localised filename so the user has info about which version
        # etc that it came from
        #
        file_name = self.object.document.executed_file.name

        split_file_name = os.path.split(file_name)[-1]
        filename_no_ext, ext = os.path.splitext(split_file_name)

        try:
            #
            # Try read it from teh local file first
            #
            resp = HttpResponse(self.object.read_local_file(), content_type='application/{ext}'.format(ext=ext))
        except:
            #
            # If we dont have it locally then read it from s3
            #
            resp = HttpResponse(self.object.document.executed_file.read(), content_type='application/{ext}'.format(ext=ext))

        resp['Content-Disposition'] = 'attachment; filename="{file_name}{ext}"'.format(file_name=filename_no_ext, ext=ext)

        return resp

#
# @TODO refactor this to use user_passes_test decorator and ensure that the user is in the reviewers set
#
class ApproveRevisionView(DetailView):
    queryset = ReviewDocument.objects.prefetch_related().all()

    def get_object(self):
        self.object = super(ApproveRevisionView, self).get_object()
        self.matter = self.object.document.item.matter

        _authenticate(request=self.request, obj=self.object, matter=self.matter, **self.kwargs)

        return self.object

    def approve(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.matter.actions.user_revision_review_complete(item=self.object.document.item, user=request.user,
                                                          revision=self.object.document)

        self.object.complete()
        return HttpResponseRedirect(success_url)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ApproveRevisionView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.approve(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('request:list')
