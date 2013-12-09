# -*- coding: utf-8 -*-
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.views.generic import FormView

from .models import Workspace

import re


class WorkspaceToolMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.workspace = get_object_or_404(Workspace, slug=self.kwargs.get('workspace'))
        self.tool = get_object_or_404(self.workspace.tools, slug=self.kwargs.get('tool'))

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


class WorkspaceToolFormMixin(WorkspaceToolMixin, FormView):
    def get_form_class(self):
        """
        Returns the form associated with the tool.
        """
        return self.tool.form

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(WorkspaceToolFormMixin, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'workspace': self.workspace
        })
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(WorkspaceToolFormMixin, self).get_initial()
        if self.object:
            initial.update(**self.object.get_form_data())
        return initial


class WorkspaceToolModelMixin(object):
    def get_form_data(self):
        """
        Returns the initial data to use for the associated form.
        """
        TIME_RE = re.compile(r'^\d{2}:\d{2}:\d{2}')
        DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}(?!T)')
        DATETIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T')

        data = self.data.copy()
        for key, value in data.iteritems():
            if TIME_RE.match(str(value)):
                data[key] = datetime.strptime(value, '%H-%M:%S')

            if DATE_RE.match(str(value)):
                data[key] = datetime.strptime(value, '%Y-%m-%d')

            if DATETIME_RE.match(str(value)):
                data[key] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')

        return data
