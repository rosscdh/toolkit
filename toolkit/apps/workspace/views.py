# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic import (FormView,
                                  ListView,
                                  CreateView,
                                  UpdateView,
                                  DetailView)

from toolkit.mixins import AjaxFormView, AjaxModelFormView, ModalView

from .models import Workspace, Tool, InviteKey
from .forms import WorkspaceForm, AddWorkspaceTeamMemberForm, InviteUserForm
from .mixins import WorkspaceToolViewMixin, WorkspaceToolFormViewMixin, IssueSignalsMixin

from .services import PDFKitService  # , HTMLtoPDForPNGService

import datetime
import logging
logger = logging.getLogger('django.request')


class AddUserToWorkspace(ModalView, AjaxFormView, FormView):
    form_class = AddWorkspaceTeamMemberForm

    def dispatch(self, request, *args, **kwargs):
        self.workspace = get_object_or_404(Workspace, slug=self.kwargs.get('slug'))
        return super(AddUserToWorkspace, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AddUserToWorkspace, self).get_context_data(**kwargs)
        context.update({
            'workspace': self.workspace,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(AddUserToWorkspace, self).get_form_kwargs()
        kwargs.update({
            'workspace': self.workspace
        })
        return kwargs

    def get_success_url(self):
        return reverse('workspace:view', kwargs={'slug': self.workspace.slug})

    def form_valid(self, form):
        # save the form
        user, is_new = form.save()
        self.workspace.participants.add(user)

        if is_new is True:
            messages.success(self.request, 'You have sucessfully added a new user "%s" to the workspace' % user)
        else:
            messages.success(self.request, 'You have sucessfully added "%s" to the workspace' % user)

        return super(AddUserToWorkspace, self).form_valid(form)


class CreateWorkspaceView(ModalView, AjaxModelFormView, CreateView):
    form_class = WorkspaceForm

    def dispatch(self, request, *args, **kwargs):
        # ensure that only lawyers can create
        if request.user.profile.is_lawyer is False:
            messages.error(request, 'Sorry, you must be an Attorney to access this')
            return HttpResponseRedirect(reverse('dash:default'))

        return super(CreateWorkspaceView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        response = super(CreateWorkspaceView, self).form_valid(form)

        # add lawyer
        self.object.lawyer = self.request.user
        self.object.save(update_fields=['lawyer'])

        # add user as participant
        self.object.participants.add(self.request.user)

        # @BUSINESS_RULE - 83(b) is added by default
        # add the 83b tool by default
        tool_83b = Tool.objects.get(slug='83b-election-letters')
        self.object.tools.add(tool_83b)

        messages.success(self.request, 'You have sucessfully created a new workspace')

        return response


class WorkspaceToolObjectsListView(WorkspaceToolViewMixin, ListView):
    """
    Show a list of objects associated with the particular tool type
    """
    model = Tool

    def get_context_data(self, **kwargs):
        context = super(WorkspaceToolObjectsListView, self).get_context_data(**kwargs)
        context.update({
            # if there are no tool.userclass_that_can_create defined then anyone can create
            # however we need to ensure that only the specified classes can create
            'can_create': True if not self.tool.userclass_that_can_create or self.request.user.profile.user_class in self.tool.userclass_that_can_create else False
        })
        return context


class CreateWorkspaceToolObjectView(WorkspaceToolFormViewMixin, CreateView):
    """
    View to create a specific Tool Object
    """
    context_object_name = 'item'
    model = Tool

    def get_queryset(self):
        qs = super(CreateWorkspaceToolObjectView, self).get_queryset()
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

        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save()
        return super(CreateWorkspaceToolObjectView, self).form_valid(form)


class UpdateViewWorkspaceToolObjectView(WorkspaceToolFormViewMixin, UpdateView):
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

        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save()
        return super(UpdateViewWorkspaceToolObjectView, self).form_valid(form)


class InviteClientWorkspaceToolObjectView(IssueSignalsMixin, WorkspaceToolViewMixin, UpdateView):
    model = InviteKey
    form_class = InviteUserForm
    template_name = 'workspace/workspace_tool_invite.html'

    def get_success_url(self):
        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.tool_instance.slug})

    def get_object(self, queryset=None):
        self.tool_instance = get_object_or_404(self.get_queryset(), slug=self.kwargs.get('slug'))

        obj, is_new = self.model.objects.get_or_create(invited_user=self.tool_instance.user,
                                                       inviting_user=self.request.user,
                                                       tool=self.tool,
                                                       tool_object_id=self.tool_instance.pk,
                                                       next=self.request.build_absolute_uri(self.tool_instance.get_edit_url()))
        return obj

    def get_form_kwargs(self):
        kwargs = super(InviteClientWorkspaceToolObjectView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'tool_instance': self.tool_instance,
            'key_instance': self.object
        })

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(InviteClientWorkspaceToolObjectView, self).get_context_data(**kwargs)
        context.update({
            'item': self.tool_instance,
            'request': self.request,
            'tool_instance': self.tool_instance,
            'key_instance': self.object
        })
        return context

    def form_valid(self, form):
        result = super(InviteClientWorkspaceToolObjectView, self).form_valid(form)
        self.issue_signals(request=self.request, instance=self.tool_instance, name='lawyer_invite_customer')  # NB teh tool_instance and NOT self.instance
        return result


class WorkspaceToolObjectPreviewView(WorkspaceToolViewMixin, DetailView):
    context_object_name = 'item'
    model = Tool
    template_name_suffix = '_tool_preview'


class WorkspaceToolObjectDisplayView(WorkspaceToolViewMixin, DetailView):
    context_object_name = 'item'
    model = Tool
    template_name = 'workspace/workspace_tool_preview.html'

    def render_to_response(self, context, **response_kwargs):
        html = self.object.html(user=self.request.user, request=self.request)
        pdfpng_service = PDFKitService(html=html)  # HTMLtoPDForPNGService(html=html)
        resp = HttpResponse(content_type='application/pdf')
        return pdfpng_service.pdf(template_name=self.object.pdf_template_name, file_object=resp)


class WorkspaceToolObjectDownloadView(IssueSignalsMixin, WorkspaceToolObjectDisplayView):
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
