# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.views.generic import FormView, UpdateView

from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EightyThreeB
from .forms import EightyThreeBForm, TrackingCodeForm


class CreateEightyThreeBView(FormView):
    form_class = EightyThreeBForm
    template_name = 'eightythreeb/eightythreeb_form.html'


class TrackingCodeView(IssueSignalsMixin, UpdateView):
    model = EightyThreeB
    form_class = TrackingCodeForm

    def form_valid(self, form):
        """
        Issue the object signals on save
        """
        self.object = form.save()
        self.issue_signals(request=self.request, instance=self.object)
        return super(TrackingCodeView, self).form_valid(form)
