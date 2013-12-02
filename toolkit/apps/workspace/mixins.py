# -*- coding: utf-8 -*-
from .models import Workspace


class WorkspaceToolMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.workspace = Workspace.objects.get(slug=self.kwargs.get('workspace'))
        self.tool = self.workspace.tools.filter(slug=self.kwargs.get('tool')).first()

        return super(WorkspaceToolMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.tool.model.objects.filter(workspace=self.workspace)

    def get_context_data(self, **kwargs):
        context = super(WorkspaceToolMixin, self).get_context_data(**kwargs)
        context.update({
            'workspace': self.workspace,
            'tool': self.tool,
        })
        return context
