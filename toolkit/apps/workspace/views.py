# -*- coding: utf-8 -*-
from django.views.generic import FormView

from .forms import WorkspaceForm


class CreateWorkspaceView(FormView):
    form_class = WorkspaceForm
    template_name = 'workspace/create.html'
