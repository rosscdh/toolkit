# -*- coding: utf-8 -*-
from django.views.generic import FormView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.detail import SingleObjectMixin

from toolkit.apps.me.views import LawyerLetterheadView
from toolkit.apps.workspace.mixins import IssueSignalsMixin

from .models import EngagementLetter, Attachment
from .forms import LawyerEngagementLetterTemplateForm, SignEngagementLetterForm


class SetupEngagementLetterTemplateView(IssueSignalsMixin, LawyerLetterheadView):
    """
    View to allow the lawyer to setup their engagement letter text
    Overrides the lawyer letterhead view and form
    """
    template_name = 'engageletter/setup_engageletter_form.html'
    form_class = LawyerEngagementLetterTemplateForm

    def get_initial(self):
        kwargs = super(SetupEngagementLetterTemplateView, self).get_initial()
        #
        # set the engageletter which is the actual obejct instance
        #
        self.engageletter = get_object_or_404(EngagementLetter, slug=self.kwargs.get('slug'))

        # @TODO load the customised lawyer letter
        try:
            body = Attachment.objects.get(tool=self.engageletter).body

        except Attachment.DoesNotExist:
            body = self.engageletter.template_source(template_name='engageletter/doc/body.html')

        kwargs.update({
            'body': body,
        })
        return kwargs

    def get_form_kwargs(self):
        """
        Update the engageletter object to the form kwargs because in this view
        "object" is UserProfile and not engageletter
        """
        kwargs = super(SetupEngagementLetterTemplateView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'instance': self.engageletter,
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        kwargs = super(SetupEngagementLetterTemplateView, self).get_context_data(*args, **kwargs)
        kwargs.update({
            'engageletter': self.engageletter
        })
        return kwargs

    def form_valid(self, form):
        """
        Issue the object signals on save
        """
        form.save()  # manually call save
        return HttpResponseRedirect(form.get_success_url())


class SignAndSendEngagementLetterView(SingleObjectMixin, FormView):
    model = EngagementLetter
    form_class = SignEngagementLetterForm
    template_name = 'engageletter/sign_engageletter.html'

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()
        kwargs = super(SignAndSendEngagementLetterView, self).get_context_data(*args, **kwargs)
        kwargs.update({
            'workspace': self.object.workspace,
            'tool': self.object.workspace.tools.filter(slug=self.object.tool_slug).first(),
        })
        return kwargs

    def get_success_url(self):
        return self.object.markers.marker('customer_sign_and_send').get_action_url()

    def form_valid(self, form):
        self.object = self.get_object()
        #
        # Send the object for signing
        #
        self.object.send_for_signing()
        #
        # Issue the signals
        #
        self.object.markers.marker('customer_sign_and_send').issue_signals(request=self.request, instance=self.object, actor=self.request.user)

        return super(SignAndSendEngagementLetterView, self).form_valid(form=form)
