# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect

from .services import CrocodocLoaderService

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

        #
        # Use the loader to get the crocodoc documet present and available
        # service provides a dict with the appropriate variables includeing 
        # crocodoc_view_url
        #
        kwarg_service = CrocodocLoaderService(user=self.request.user, reviewdocument=self.object)
        kwargs.update(kwarg_service.process())

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

        self.object.document.item.matter.actions.user_downloaded_revision(item=self.object.document.item,
                                                                          user=self.request.user,
                                                                          revision=self.object.document)

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
