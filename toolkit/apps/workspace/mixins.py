# -*- coding: utf-8 -*-
from datetime import datetime

from django import forms
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from crispy_forms.helper import FormHelper

from .models import Workspace

import re
import logging
logger = logging.getLogger('django.request')


class WorkspaceToolViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.workspace = get_object_or_404(Workspace, slug=self.kwargs.get('workspace'))
        self.tool = get_object_or_404(self.workspace.tools, slug=self.kwargs.get('tool'))

        return super(WorkspaceToolViewMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.tool.model.objects.filter(workspace=self.workspace)

    def get_context_data(self, **kwargs):
        context = super(WorkspaceToolViewMixin, self).get_context_data(**kwargs)
        context.update({
            'workspace': self.workspace,
            'tool': self.tool,
        })
        return context


class WorkspaceToolFormViewMixin(WorkspaceToolViewMixin, FormView):
    def get_form_class(self):
        """
        Returns the form associated with the tool.
        """
        return self.tool.get_form(user=self.request.user)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(WorkspaceToolFormViewMixin, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'workspace': self.workspace
        })
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(WorkspaceToolFormViewMixin, self).get_initial()
        if self.object:
            initial.update(**self.object.get_form_data())
        return initial

    def get_template_names(self):
        """
        Returns the form template names associated with the tool.
        """
        names = []

        if hasattr(self.tool, 'model'):
            opts = self.tool.model._meta
            names.append("%s/%s%s.html" % (opts.app_label, opts.model_name, self.template_name_suffix))

        return names


class WorkspaceToolFormMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # pop this as we are not using a model form
        self.request = kwargs.pop('request')
        self.workspace = kwargs.pop('workspace')

        self.user = None
        if self.request is not None:
            self.user = self.request.user

        self.helper = FormHelper()

        self.helper.attrs = {
            'parsley-validate': '',
        }
        self.helper.form_show_errors = False

        super(WorkspaceToolFormMixin, self).__init__(*args, **kwargs)


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


class IssueSignalsMixin(object):
    def issue_signals(self, request, instance, **kwargs):
        """
        issue the base_signal signal to handle any change events
        """
        logger.debug('Issuing signals for WorkspaceToolObjectDownloadView')

        if hasattr(instance, 'base_signal'):
            instance.base_signal.send(sender=request, instance=instance, actor=request.user, **kwargs)
            logger.info('Issued signals for %s (%s)' % (instance, request.user))

        else:
            logger.error('The "%s" object must define a base_signal property which returns the app base signal' % instance._meta.model.__name__)
