# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from django.views.generic import (ListView,
                                  FormView,
                                  CreateView)

from toolkit.mixins import AjaxFormView, AjaxModelFormView, ModalView

from ..models import Workspace, Tool
from ..forms import WorkspaceForm, AddWorkspaceTeamMemberForm

import logging
logger = logging.getLogger('django.request')


class CreateWorkspaceView(ModalView, AjaxModelFormView, CreateView):
    form_class = WorkspaceForm

    def dispatch(self, request, *args, **kwargs):
        # ensure that only lawyers can create
        if request.user.profile.is_lawyer is False:
            messages.error(request, 'Sorry, you must be an Attorney to access this')
            return HttpResponseRedirect(reverse('matter:list'))

        return super(CreateWorkspaceView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super(CreateWorkspaceView, self).get_form_kwargs()
        kwargs.update({'lawyer': self.request.user})
        return kwargs

    def form_valid(self, form):
        workspace = super(CreateWorkspaceView, self).form_valid(form)
        # @BUSINESS_RULE - 83(b) is added by default
        # add the 83b tool by default
        tool_83b = Tool.objects.get(slug='83b-election-letters')
        self.object.tools.add(tool_83b)

        messages.success(self.request, 'You have sucessfully created a new workspace')

        return workspace


class WorkspaceToolsView(ListView):
    """
    List Available tools
    """
    model = Tool

    def get_context_data(self, **kwargs):
        context = super(WorkspaceToolsView, self).get_context_data(**kwargs)
        context.update({
            'workspace': get_object_or_404(Workspace, slug=self.kwargs.get('workspace'))
        })
        return context


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
