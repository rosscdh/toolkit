# -*- coding: utf-8 -*-
from django.contrib import messages
from django.views.generic import FormView
from django.core.urlresolvers import reverse

from .forms import WorkspaceForm


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