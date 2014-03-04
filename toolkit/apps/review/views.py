# -*- coding: utf-8 -*-
from django.views.generic import DetailView

from dj_crocodoc.services import CrocoDocConnectService

from .models import ReviewDocument


class ReviewRevisionView(DetailView):
    """
    View to allow an authenticated user to view a crocodoc url that is connected
    to a core.attachment revision
    """
    model = ReviewDocument
    template_name = 'review/review.html'

    def get_context_data(self, **kwargs):
        kwargs = super(ReviewRevisionView, self).get_context_data(**kwargs)

        crocodoc = CrocoDocConnectService(document_object=self.object.document,
                                          app_label='attachment',
                                          field_name='executed_file',
                                          upload_immediately=True)

        kwargs.update({
            'crocodoc': crocodoc.obj.crocodoc_service,
            'crocodoc_view_url': crocodoc.obj.crocodoc_service.view_url(),
        })

        return kwargs