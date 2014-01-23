# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from toolkit.apps.me.views import LawyerLetterheadView

from .models import EngagementLetter
from .forms import LawyerEngagementLetterTemplateForm, SignEngagementLetterForm


class SetupEngagementLetterView(LawyerLetterheadView):
    """
    View to allow the lawyer to setup their engagement letter text
    Overrides the lawyer letterhead view and form
    """
    template_name = 'engageletter/setup_engageletter_form.html'
    form_class = LawyerEngagementLetterTemplateForm

    def get_initial(self):
        kwargs = super(SetupEngagementLetterView, self).get_initial()

        engageletter = get_object_or_404(EngagementLetter, slug=self.kwargs.get('slug'))

        kwargs.update({
            'body': engageletter.template_source,
        })
        return kwargs


class SignAndSendEngagementLetterView(SingleObjectMixin, FormView):
    model = EngagementLetter
    form_class = SignEngagementLetterForm
    template_name = 'engageletter/sign_engageletter.html'

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()
        return super(SignAndSendEngagementLetterView, self).get_context_data(*args, **kwargs)
