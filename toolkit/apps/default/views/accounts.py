# -*- coding: utf-8 -*-
from django.views.generic import FormView

from ..forms import UserAccountForm, UserChangePasswordForm


class UserAccountView(FormView):
    form_class = UserAccountForm


class UserChangePasswordView(FormView):
    form_class = UserChangePasswordForm