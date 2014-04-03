# -*- coding: utf-8 -*-
from django.http import Http404
from django.core import signing
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, UpdateView, TemplateView
from django.views.generic.edit import BaseUpdateView
from django.shortcuts import get_object_or_404

from toolkit.apps.me.signals import send_welcome_email
from toolkit.apps.default.models import UserProfile
from toolkit.mixins import AjaxModelFormView
#from toolkit.apps.default.views import LogOutMixin

from .mailers import ValidateEmailMailer

from .forms import (ConfirmAccountForm,
                    ChangePasswordForm,
                    AccountSettingsForm,
                    LawyerLetterheadForm)

import json

User = get_user_model()


class ConfirmAccountView(UpdateView):
    form_class = ConfirmAccountForm
    model = User
    template_name = 'user/settings/account.html'

    def dispatch(self, request, *args, **kwargs):

        # check to see if they have already set their password
        if request.user.is_authenticated() and request.user.password not in [None, '', '!']:
            messages.warning(request, 'It looks like you have already confirmed your account. No need to access that form.')
            return redirect(reverse('public:home'))

        return super(ConfirmAccountView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # get target user, profile
        profile = self.request.user.profile

        # if user is new, has not set password
        sent_welcome_email = profile.data.get('sent_welcome_email', False)
        if sent_welcome_email is False:
            #
            # Send welcome email
            #
            send_welcome_email.send(sender=self.request.user._meta.model, instance=self.request.user, created=True)

            # store the json reciept
            profile.data['sent_welcome_email'] = True
            profile.save(update_fields=['data'])

        return super(ConfirmAccountView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Thank you. You have confirmed your account')
        try:
            first_invite_key = self.request.user.invitations.all().first()
            return first_invite_key.next

        except AttributeError:
            # was no invite key
            return reverse_lazy('public:home')


class SendEmailValidationRequest(BaseUpdateView):
    def post(self, request, *args, **kwargs):
        """
        Jsut send it; if the user has already validated then we will catch that
        on the confirmation view
        """
        mailer = ValidateEmailMailer(((request.user.get_full_name(), request.user.email)))
        mailer.process(user=request.user)

        content = {
            'detail': 'Email sent'
        }
        return HttpResponse(json.dumps(content), content_type='application/json', **kwargs)


#
#class ConfirmEmailValidationRequest(LogOutMixin, TemplateView):
#
# The commented out option is very secure
#
#
class ConfirmEmailValidationRequest(TemplateView):
    template_name = None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        try:
            pk = signing.loads(kwargs['token'], salt=settings.SECRET_KEY)
        except signing.BadSignature:
            raise Http404

        self.user = get_object_or_404(get_user_model(), pk=pk)
        profile = self.user.profile
        profile.validated_email = True
        profile.save(update_fields=['data'])

        messages.success(self.request, 'Thanks. You have confirmed your email address.')

        return redirect('/')


class AccountSettingsView(UpdateView):
    form_class = AccountSettingsForm
    model = User
    success_url = reverse_lazy('me:settings')
    template_name = 'user/settings/account.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Success. You have updated your account')
        return super(AccountSettingsView, self).get_success_url()


class ChangePasswordView(AjaxModelFormView, FormView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('me:settings')
    template_name = 'user/settings/change-password.html'

    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs['user'] = self.get_user()
        return kwargs

    def get_user(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success. You have changed your password')
        return super(ChangePasswordView, self).form_valid(form)


class LawyerLetterheadView(UpdateView):
    """
    View that handles the Letterhead Setup Form for Lawyers
    get the initial form data form the users profile.data
    form will save that data
    """
    form_class = LawyerLetterheadForm
    model = UserProfile
    template_name = 'lawyer/lawyerletterhead_form.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_initial(self):
        kwargs = super(LawyerLetterheadView, self).get_initial()

        profile = self.request.user.profile

        kwargs.update({
            'firm_name': profile.data.get('firm_name'),
            'firm_address': profile.data.get('firm_address'),
            'firm_logo': profile.data.get('firm_logo'),
        })
        return kwargs

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET.get('next')
        else:
            return self.object.get_absolute_url() if self.object is not None and hasattr(self.object, 'get_absolute_url') else reverse('matter:list')

    def get_form_kwargs(self):
        kwargs = super(LawyerLetterheadView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs
