# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView

from toolkit.apps.workspace.models import Workspace


class DashView(TemplateView):
    template_name = 'dash/dash.html'

    def get_context_data(self, **kwargs):
        context = super(DashView, self).get_context_data(**kwargs)

        context.update({
            'dash': True,
            'workspaces': Workspace.objects.mine(user=self.request.user)
        })

        return context
