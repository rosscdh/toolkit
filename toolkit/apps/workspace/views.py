# -*- coding: utf-8 -*-
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView

from toolkit.apps.eightythreeb.forms import EightyThreeBForm

from .forms import WorkspaceForm
from .models import Workspace, Tool


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


class WorkspaceToolObjectsListView(ListView):
    """
    Show a list of objects associated with the particular tool type
    """
    model = Tool
    template_name = 'workspace/workspace_tool_list.html'

    def get_queryset(self):
        self.workspace = Workspace.objects.get(slug=self.kwargs.get('workspace'))
        self.tool = self.workspace.tools.filter(slug=self.kwargs.get('tool')).first()

        # get the tools for the list by worksapce
        return self.tool.model.objects.filter(workspace=self.workspace)

    def get_context_data(self, **kwargs):
        context = super(WorkspaceToolObjectsListView, self).get_context_data(**kwargs)
        context.update({
            'workspace': self.workspace,
            'tool': self.tool,
        })
        return context


class CreateWorkspaceToolObjectView(CreateView):
    """
    View to create a specific Tool Object
    """
    model = Tool
    template_name = 'workspace/workspace_tool_form.html'
    form_class = EightyThreeBForm

    def dispatch(self, request, *args, **kwargs):
        self.workspace = Workspace.objects.get(slug=self.kwargs.get('workspace'))
        self.tool = self.workspace.tools.filter(slug=self.kwargs.get('tool')).first()

        return super(CreateWorkspaceToolObjectView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.tool.model.objects.filter(workspace=self.workspace, user=self.request.user).first()

    def get_success_url(self):
        return reverse('workspace:tool_object_list', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug})

    def get_form_kwargs(self):
        kwargs = super(CreateWorkspaceToolObjectView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'workspace': self.workspace
        })
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super(CreateWorkspaceToolObjectView, self).form_valid(form)


class UpdateViewWorkspaceToolObjectView(UpdateView):
    """
    View to edit a specific Tool Object
    """
    model = Tool
    template_name = 'workspace/workspace_tool_form.html'
    form_class = EightyThreeBForm

    def dispatch(self, request, *args, **kwargs):
        self.workspace = Workspace.objects.get(slug=self.kwargs.get('workspace'))
        self.tool = self.workspace.tools.filter(slug=self.kwargs.get('tool')).first()

        return super(UpdateViewWorkspaceToolObjectView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.tool.model.objects.filter(workspace=self.workspace)

    def get_success_url(self):
        return reverse('workspace:tool_object_list', kwargs={'workspace': self.workspace.slug, 'tool': self.tool.slug})

    def get_form_kwargs(self):
        kwargs = super(UpdateViewWorkspaceToolObjectView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'workspace': self.workspace
        })
        return kwargs

    def get_initial(self):
        initial = super(UpdateViewWorkspaceToolObjectView, self).get_initial()
        initial.update(**self.object.data)
        return initial

    def form_valid(self, form):
        self.object = form.save()
        return super(UpdateViewWorkspaceToolObjectView, self).form_valid(form)
