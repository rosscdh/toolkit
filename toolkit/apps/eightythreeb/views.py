# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.views.generic import FormView, UpdateView

from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EightyThreeB
from .forms import TrackingCodeForm


class TrackingCodeView(IssueSignalsMixin, UpdateView):
    model = EightyThreeB
    form_class = TrackingCodeForm

    def form_valid(self, form):
        """
        Issue the object signals on save
        """
        self.object = form.save()
        self.issue_signals(request=self.request, instance=self.object, name='mail_to_irs_tracking_code')
        return super(TrackingCodeView, self).form_valid(form)
