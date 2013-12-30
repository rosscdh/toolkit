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

from .models import Workspace, Tool, InviteKey
from .forms import WorkspaceForm, AddWorkspaceTeamMemberForm, InviteUserForm
from .mixins import WorkspaceToolViewMixin, WorkspaceToolFormViewMixin, IssueSignalsMixin

from .services import PDFKitService  # , HTMLtoPDForPNGService

import logging
logger = logging.getLogger('django.request')


class AddUserToWorkspace(CreateView):
    template_name = 'workspace/workspace_user_form.html'
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


class CreateWorkspaceView(FormView):
    form_class = WorkspaceForm
    template_name = 'workspace/workspace_form.html'

    def dispatch(self, request, *args, **kwargs):
        # ensure that only lawyers can create
        if request.user.profile.is_lawyer is False:
            messages.error(request, 'Sorry, you must be an Attorney to access this')
            return HttpResponseRedirect(reverse('dash:default'))

        return super(CreateWorkspaceView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dash:default')

    def form_invalid(self, form):
        messages.error(self.request, 'Sorry, there was an error %s' % form.errors)
        return super(CreateWorkspaceView, self).form_invalid(form)

    def form_valid(self, form):
        # save the form
        workspace = form.save()
        workspace.participants.add(self.request.user)

        tool_83b = Tool.objects.get(slug='83b-election-letters')
        workspace.tools.add(tool_83b)

        messages.success(self.request, 'You have sucessfully created a new workspace')
        return super(CreateWorkspaceView, self).form_valid(form)


class WorkspaceToolObjectsListView(WorkspaceToolViewMixin, ListView):
    """
    Show a list of objects associated with the particular tool type
    """
    model = Tool


class CreateWorkspaceToolObjectView(WorkspaceToolFormViewMixin, CreateView):
    """
    View to create a specific Tool Object
    """
    model = Tool

    def get_queryset(self):
        qs = super(CreateWorkspaceToolObjectView, self).get_queryset()
        return qs.filter(user=self.request.user).first()

    def get_success_url(self):
        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save()
        return super(CreateWorkspaceToolObjectView, self).form_valid(form)


class UpdateViewWorkspaceToolObjectView(WorkspaceToolFormViewMixin, UpdateView):
    """
    View to edit a specific Tool Object
    """
    model = Tool

    def get_success_url(self):
        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug, 'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save()
        return super(UpdateViewWorkspaceToolObjectView, self).form_valid(form)


class InviteClientWorkspaceToolObjectView(IssueSignalsMixin, WorkspaceToolViewMixin, UpdateView):
    model = InviteKey
    form_class = InviteUserForm

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
            'request': self.request,
            'tool_instance': self.tool_instance,
            'key_instance': self.object
        })
        return context

    def form_valid(self, form):
        email = form.save()  # not used
        self.issue_signals(request=self.request, instance=self.tool_instance, name='lawyer_invite_customer')  # NB teh tool_instance and NOT self.instance

        return super(InviteClientWorkspaceToolObjectView, self).form_valid(form)


class WorkspaceToolObjectPreviewView(WorkspaceToolViewMixin, DetailView):
    model = Tool
    template_name_suffix = '_tool_preview'


class WorkspaceToolObjectDisplayView(WorkspaceToolViewMixin, DetailView):
    model = Tool
    template_name = 'workspace/workspace_tool_preview.html'

    def render_to_response(self, context, **response_kwargs):
        html = self.object.html(user=self.request.user, request=self.request)
        pdfpng_service = PDFKitService(html=html)  # HTMLtoPDForPNGService(html=html)
        resp = HttpResponse(content_type='application/pdf')
        return pdfpng_service.pdf(template_name=self.object.template_name, file_object=resp)


class WorkspaceToolObjectDownloadView(IssueSignalsMixin, WorkspaceToolObjectDisplayView):
    model = Tool

    def render_to_response(self, context, **response_kwargs):
        html = self.object.html(user=self.request.user, request=self.request)
        pdfpng_service = PDFKitService(html=html)  # HTMLtoPDForPNGService(html=html)
        resp = HttpResponse(content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="{filename}.pdf"'.format(filename=self.object.filename)

        self.issue_signals(request=self.request, instance=self.object)

        return pdfpng_service.pdf(template_name=self.object.template_name, file_object=resp)
