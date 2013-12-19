# -*- coding: utf-8 -*-
from django.views.generic import FormView

from ..forms import UserAccountForm, UserChangePasswordForm


class UserAccountView(FormView):
    form_class = UserAccountForm
    template_name = 'public/settings/account.html'


class UserChangePasswordView(FormView):
    form_class = UserChangePasswordForm
    template_name = 'public/settings/password.html'
