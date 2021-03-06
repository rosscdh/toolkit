# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files import File
from django.contrib import messages
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404

from ajaxuploader.views import AjaxFileUploader

from toolkit.mixins import AjaxModelFormView, ModalView
from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EightyThreeB
from .forms import TrackingCodeForm, AttachmentForm

import os
import json
import logging
logger = logging.getLogger('django.request')


class TrackingCodeView(IssueSignalsMixin, ModalView, AjaxModelFormView, UpdateView):
    form_class = TrackingCodeForm
    model = EightyThreeB

    def form_valid(self, form):
        """
        Issue the object signals on save
        """
        response = super(TrackingCodeView, self).form_valid(form)
        self.issue_signals(request=self.request, instance=self.object, name='mail_to_irs_tracking_code')

        messages.success(self.request, 'Successfully added a Tracking Code')

        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class AttachmentView(IssueSignalsMixin, UpdateView):
    context_object_name = 'item'
    model = EightyThreeB
    form_class = AttachmentForm
    template_name_suffix = '_attachment_form'

    def get_context_data(self, **kwargs):
        context = super(AttachmentView, self).get_context_data(**kwargs)

        workspace = self.object.workspace
        tool = get_object_or_404(workspace.tools, slug=self.object.tool_slug)

        context.update({
            'tool': tool,
            'workspace': workspace
        })

        return context

    def form_valid(self, form):
        """
        Issue the object signals on save
        """
        self.object = form.save()
        self.issue_signals(request=self.request, instance=self.object, name='copy_uploaded')
        return super(AttachmentView, self).form_valid(form)


class UploadFileView(IssueSignalsMixin, UpdateView):
    """
    Override the uploader and cater to the multiple file associations
    @TODO turn this into a service
    """
    model = EightyThreeB
    uploader = None

    def __init__(self, *args, **kwargs):
        super(UploadFileView, self).__init__(*args, **kwargs)
        self.uploader = AjaxFileUploader()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Upload the File using the ajax_uploader object
        response = self.uploader._ajax_upload(request, *args, **kwargs)
        if response.status_code in [200]:
            # success
            data = json.loads(response.content)
            base_path, filename = os.path.split(data.get('path'))
            # create and upload to s3
            with open(os.path.join(settings.MEDIA_ROOT, 'uploads', filename)) as file_path:
                uploaded_file = File(file_path)
                attachment = self.object.attachment_set.create(eightythreeb=self.object)
                attachment.attachment = uploaded_file
                attachment.save()

            os.remove(uploaded_file.name)

            data['path'] = attachment.attachment.url
            response.content = json.dumps(data)

            # send signal
            self.issue_signals(request=request, instance=self.object, name='copy_uploaded')

        return response
