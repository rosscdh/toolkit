# -*- coding: utf-8 -*-
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from .models import EngagementLetter
from .forms import SignEngagementLetterForm


class SignAndSendEngagementLetterView(SingleObjectMixin, FormView):
    model = EngagementLetter
    form_class = SignEngagementLetterForm
    template_name = 'engageletter/sign_engageletter.html'

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()
        return super(SignAndSendEngagementLetterView, self).get_context_data(*args, **kwargs)