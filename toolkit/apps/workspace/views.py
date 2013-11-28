# -*- coding: utf-8 -*-
from django.contrib import messages
from django.views.generic import FormView, ListView, CreateView, UpdateView
from django.core.urlresolvers import reverse

from toolkit.apps.eightythreeb.forms import EightyThreeBForm

from .forms import WorkspaceForm
from .models import Workspace, Tool


class CreateWorkspaceView(FormView):
    form_class = WorkspaceForm
    template_name = 'workspace/workspace_form.html'

    def get_success_url(self):
        return reverse('dash:default')

    def form_invalid(self, form):
        messages.error(self.request, 'Sorry, there was an error %s' % form.errors)
        return super(CreateWorkspaceView, self).form_invalid(form)

    def form_valid(self, form):
        # save the form
        form.save()

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


class UpdateViewWorkspaceToolObjectView(UpdateView):
    """
    View to edit a specific Tool Object
    """
    model = Tool
    template_name = 'workspace/workspace_tool_form.html'
    form_class = EightyThreeBForm
