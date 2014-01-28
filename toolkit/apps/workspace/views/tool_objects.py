# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template.defaultfilters import slugify
from django.template import TemplateDoesNotExist
from django.http import HttpResponse

from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DetailView)

from ..models import Tool, InviteKey
from ..forms import InviteUserForm
from ..mixins import WorkspaceToolViewMixin, WorkspaceToolFormViewMixin, IssueSignalsMixin
from ..services import PDFKitService  # , HTMLtoPDForPNGService

import datetime
import logging
logger = logging.getLogger('django.request')


class ToolObjectListView(WorkspaceToolViewMixin, ListView):
    """
    Show a list of objects associated with the particular tool type
    """
    model = Tool

    def get_context_data(self, **kwargs):
        context = super(ToolObjectListView, self).get_context_data(**kwargs)

        # standard create object url
        create_url = reverse('workspace:tool_object_new', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug})

        action_url = self.tool.markers.prerequisite_next_url(workspace=self.workspace)
        if action_url is not None:
            # append the next portion
            create_url = '%s?next=%s' % (action_url, self.request.get_full_path())

        context.update({
            # if there are no tool.userclass_that_can_create defined then anyone can create
            # however we need to ensure that only the specified classes can create
            'can_create': True if not self.tool.userclass_that_can_create or self.request.user.profile.user_class in self.tool.userclass_that_can_create else False,
            'create_url': create_url,
        })
        return context


class CreateToolObjectView(WorkspaceToolFormViewMixin, CreateView):
    """
    View to create a specific Tool Object
    """
    context_object_name = 'item'
    model = Tool

    def get_queryset(self):
        qs = super(CreateToolObjectView, self).get_queryset()
        return qs.filter(user=self.request.user).first()

    def get_success_url(self):
        """
        Generic view now tests for the form having a get_success_url and because
        the forms all extend “WorkspaceToolFormMixin” which is a forms.Form and
        not forms.Model form we need to pass instance into the method
        (as the form does not have self.instance as its not a model form)
        """
        form = self.get_form(form_class=self.get_form_class())
        if hasattr(form, 'get_success_url'):
            return form.get_success_url(instance=self.object)

        return reverse('workspace:tool_object_overview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save()
        return super(CreateToolObjectView, self).form_valid(form)


class UpdateViewToolObjectView(WorkspaceToolFormViewMixin, UpdateView):
    """
    View to edit a specific Tool Object
    """
    context_object_name = 'item'
    model = Tool

    def get_success_url(self):
        """
        Generic view now tests for the form having a get_success_url and because
        the forms all extend “WorkspaceToolFormMixin” which is a forms.Form and
        not forms.Model form we need to pass instance into the method
        (as the form does not have self.instance as its not a model form)
        """
        form = self.get_form(form_class=self.get_form_class())
        if hasattr(form, 'get_success_url'):
            return form.get_success_url(instance=self.object)

        return reverse('workspace:tool_object_overview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save()
        return super(UpdateViewToolObjectView, self).form_valid(form)


class InviteClientToolObjectView(IssueSignalsMixin, WorkspaceToolViewMixin, UpdateView):
    model = InviteKey
    form_class = InviteUserForm
    template_name = 'workspace/workspace_tool_invite.html'

    def get_success_url(self):
        return reverse('workspace:tool_object_overview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.tool_instance.slug})

    def get_object(self, queryset=None):
        self.tool_instance = get_object_or_404(self.get_queryset(), slug=self.kwargs.get('slug'))

        obj, is_new = self.model.objects.get_or_create(invited_user=self.tool_instance.user,
                                                       inviting_user=self.request.user,
                                                       tool=self.tool,
                                                       tool_object_id=self.tool_instance.pk,
                                                       next=self.request.build_absolute_uri(self.tool_instance.get_edit_url()))
        return obj

    def get_form_kwargs(self):
        kwargs = super(InviteClientToolObjectView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'tool_instance': self.tool_instance,
            'key_instance': self.object
        })

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(InviteClientToolObjectView, self).get_context_data(**kwargs)
        context.update({
            'item': self.tool_instance,
            'request': self.request,
            'tool_instance': self.tool_instance,
            'key_instance': self.object
        })
        return context

    def form_valid(self, form):
        result = super(InviteClientToolObjectView, self).form_valid(form)
        self.issue_signals(request=self.request, instance=self.tool_instance, name='lawyer_invite_customer')  # NB teh tool_instance and NOT self.instance
        return result


class ToolObjectPreviewView(WorkspaceToolViewMixin, DetailView):
    context_object_name = 'item'
    model = Tool
    template_name_suffix = '_tool_preview'


class ToolObjectDisplayView(WorkspaceToolViewMixin, DetailView):
    context_object_name = 'item'
    model = Tool
    template_name = 'workspace/workspace_tool_preview.html'

    def render_to_response(self, context, **response_kwargs):
        html = self.object.html(user=self.request.user, request=self.request)
        pdfpng_service = PDFKitService(html=html)  # HTMLtoPDForPNGService(html=html)
        resp = HttpResponse(content_type='application/pdf')
        return pdfpng_service.pdf(template_name=self.object.pdf_template_name, file_object=resp)


class ToolObjectDownloadView(IssueSignalsMixin, ToolObjectDisplayView):
    model = Tool

    def setResponseFileDownloaderCookie(self, response):
        """
        Cookie for the jquery Plugin used for downloader
        """
        max_age = 30
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie( 'fileDownload', 'true', max_age=max_age, expires=expires )
        return response

    def render_to_response(self, context, **response_kwargs):
        html = self.object.html(user=self.request.user, request=self.request)
        pdfpng_service = PDFKitService(html=html)  # HTMLtoPDForPNGService(html=html)
        resp = HttpResponse(content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="{filename}.pdf"'.format(filename=self.object.filename)

        messages.success(self.request, 'You have sucessfully downloaded a copy of your 83(b).')

        resp = self.setResponseFileDownloaderCookie(response=resp)

        self.issue_signals(request=self.request, instance=self.object, name='customer_download_pdf')

        return pdfpng_service.pdf(template_name=self.object.pdf_template_name, file_object=resp)


class ToolObjectPostFormPreviewView(DetailView):
    """
    View used to display the PDF Preview to Lawyer/Customer
    after they have completed the tool form
    and redirect on to the next marker step
    """
    model = Tool
    slug_url_kwarg = 'tool'

    def get_object(self, queryset=None):
        """
        Get the base tool object as normal and then use its "model" property
        to return the target apps model and then reset the object to that new
        object
        """
        # get tool
        tool = super(ToolObjectPostFormPreviewView, self).get_object(queryset=queryset)
        # do a search on the tool target model
        tool_object_instance = get_object_or_404(tool.model.objects, slug=self.kwargs.get('slug'))
        
        return tool_object_instance

    def get_template_names(self):
        template_name = 'after_form_preview.html'
        try:
            return get_template('%s/%s' % (slugify(self.object._meta.model.__name__), template_name))
        except TemplateDoesNotExist:
            return get_template('%s/%s' % (slugify(self.object._meta.app_label), template_name))
        else:
            return get_template('workspace/%s' % template_name)

    def get_next_previous_urls(self):
        markers = self.object.markers
        preview_workspace_url = reverse('workspace:tool_object_overview', kwargs={'workspace': self.object.workspace.slug, 'tool': self.object.tool_slug, 'slug': self.object.slug})

        if self.request.user.profile.is_lawyer is True:
            # for Lawyer
            # get the current markers next_marker which will then
            # calculate based on Prerequisite Markers
            marker = markers.current_marker.next_marker
            return {
                'previous_url': markers.marker(val='lawyer_complete_form').get_action_url(),
                'next_url': marker.get_action_url() if 'lawyer' in marker.action_user_class and marker.action_type == marker.ACTION_TYPE.redirect else preview_workspace_url,
            }

        elif self.request.user.profile.is_customer is True:
            # for Customer
            return {
                'previous_url': markers.marker(val='customer_complete_form').get_action_url(),
                'next_url': preview_workspace_url,
            }

    def get_context_data(self, **kwargs):
        context = super(ToolObjectPostFormPreviewView, self).get_context_data(**kwargs)
        context.update(self.get_next_previous_urls())  # append the next previous urls

        workspace = self.object.workspace
        tool = get_object_or_404(workspace.tools, slug=self.object.tool_slug)

        context.update({
            'tool': tool,
            'workspace': workspace
        })

        return context
