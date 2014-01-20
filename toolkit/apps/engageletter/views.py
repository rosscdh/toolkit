# -*- coding: utf-8 -*-
from django.views.generic import FormView

from .forms import SignEngagementLetterForm


class SignAndSendEngagementLetterView(FormView):
    form_class = SignEngagementLetterForm
    template_name = 'engageletter/sign_engageletter.html'