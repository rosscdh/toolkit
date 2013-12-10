# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from .models import Workspace

import logging
logger = logging.getLogger('django.request')


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


class IssueSignalsMixin(object):
    def issue_signals(self, request, instance):
        """
        issue the base_signal signal to handle any change events
        """
        logger.debug('Issuing signals for WorkspaceToolObjectDownloadView')

        if hasattr(instance, 'base_signal'):
            instance.base_signal.send(sender=request, instance=instance, actor=request.user)
            logger.info('Issued signals for %s (%s)' % (instance, request.user))

        else:
            logger.error('The "%s" object must define a base_signal property which returns the app base signal' % instance._meta.model.__name__)