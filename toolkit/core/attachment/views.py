# -*- coding: UTF-8 -*-
import os
from django.http import HttpResponse
from django.views.generic import DetailView

from toolkit.core.attachment.models import Attachment


class DownloadAttachment(DetailView):
    """
    Class to allow a matter.participant to download an attachment
    without exposing the s3 url to anyone
    """
    queryset = Attachment.objects.prefetch_related().all()
    template_name = None

    def get_object(self):
        self.object = super(DownloadAttachment, self).get_object()
        self.item = self.object.item
        self.matter = self.item.matter

        return self.object

    def get_file_object_contents_response(self, as_attachment=True):
        #
        # Use our localised filename so the user has info about which version
        # etc that it came from
        #
        file_name = self.object.get_document().name

        split_file_name = os.path.split(file_name)[-1]
        filename_no_ext, ext = os.path.splitext(split_file_name)

        try:
            #
            # Try read it from the local file first
            #
            resp = HttpResponse(self.object.read_local_file(), content_type='application/{ext}'.format(ext=ext))

        except:
            #
            # If we dont have it locally then read it from s3
            #
            resp = HttpResponse(self.object.document.executed_file.read(), content_type='application/{ext}'.format(ext=ext))

        if as_attachment is True:
            resp['Content-Disposition'] = 'attachment; filename="{file_name}.{ext}"'.format(file_name=filename_no_ext, ext=ext)

        return resp

    def get_context_data(self, **kwargs):
        # REMEMBER not to call super here as we dont want crocdoc near this
        self.object.ensure_file()

    def render_to_response(self, context, **response_kwargs):
        resp = self.get_file_object_contents_response(as_attachment=True)

        # self.object.document.item.matter.actions.user_downloaded_revision(item=self.object.document.item,
        #                                                                   user=self.request.user,
        #                                                                   revision=self.object.document)
        return resp
