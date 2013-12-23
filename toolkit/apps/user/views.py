from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, UpdateView

from .forms import ChangePasswordForm, AccountSettingsForm


User = get_user_model()


class AccountSettingsView(UpdateView):
    form_class = AccountSettingsForm
    model = User
    success_url = reverse_lazy('me:settings')
    template_name = 'user/settings/account.html'

    def get_object(self, queryset=None):
        return self.request.user


class ChangePasswordView(FormView):
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
        return super(ChangePasswordView, self).form_valid(form)
