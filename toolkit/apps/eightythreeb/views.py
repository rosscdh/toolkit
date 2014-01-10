# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files import File
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView, DetailView

from ajaxuploader.views import AjaxFileUploader
from ajaxuploader.backends.default_storage import DefaultStorageUploadBackend

from toolkit.mixins import ModalView
from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EightyThreeB
from .forms import TrackingCodeForm, AttachmentForm

import os
import json
import logging
logger = logging.getLogger('django.request')


class Preview83bView(DetailView):
    """
    View used to display the PDF to Lawyer/Customer
    after they have completed the 83b form
    and redirect on to the next marker step
    """
    context_object_name = 'item'
    model = EightyThreeB
    template_name = 'eightythreeb/after_form_preview.html'

    def get_next_previous_urls(self):
        markers = self.object.markers
        preview_workspace_url = reverse('workspace:tool_object_preview', kwargs={'workspace': self.object.workspace.slug, 'tool': self.object.tool_slug, 'slug': self.object.slug})

        if self.request.user.profile.is_lawyer is True:
            # for Lawyer
            return {
                'previous_url': markers.marker(val='lawyer_complete_form').get_action_url(),
                'next_url': markers.next.get_action_url() if markers.next.action_type == markers.next.ACTION_TYPE.redirect else preview_workspace_url,
            }

        elif self.request.user.profile.is_customer is True:
            # for Customer
            return {
                'previous_url': markers.marker(val='customer_complete_form').get_action_url(),
                'next_url': preview_workspace_url,
            }

    def get_context_data(self, **kwargs):
        context = super(Preview83bView, self).get_context_data(**kwargs)
        context.update(self.get_next_previous_urls())  # append the next previous urls

        workspace = self.object.workspace
        tool = get_object_or_404(workspace.tools, slug=self.object.tool_slug)

        context.update({
            'tool': tool,
            'workspace': workspace
        })

        return context


class TrackingCodeView(IssueSignalsMixin, ModalView, UpdateView):
    form_class = TrackingCodeForm
    model = EightyThreeB

    def form_valid(self, form):
        """
        Issue the object signals on save
        """
        self.object = form.save()
        self.issue_signals(request=self.request, instance=self.object, name='mail_to_irs_tracking_code')
        return super(TrackingCodeView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Successfully added a Tracking Code')
        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.object.workspace.slug, 'tool': self.object.tool_slug, 'slug': self.object.slug})


class AttachmentView(IssueSignalsMixin, UpdateView):
    model = EightyThreeB
    form_class = AttachmentForm
    template_name_suffix = '_attachment_form'

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
