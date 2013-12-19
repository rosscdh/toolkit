# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.generic import UpdateView

from ..forms import UserAccountForm


class UserAccountView(UpdateView):
    form_class = UserAccountForm
    model = User
    template_name = 'public/settings.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('public:settings')


# class UserChangePasswordView(FormView):
    # form_class = UserChangePasswordForm
    # template_name = 'public/settings/password.html'
