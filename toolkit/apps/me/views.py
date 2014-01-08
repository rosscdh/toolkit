from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, UpdateView

from toolkit.apps.me.signals import send_welcome_email
from toolkit.apps.workspace.models import InviteKey

from .forms import ConfirmAccountForm, ChangePasswordForm, AccountSettingsForm


User = get_user_model()


class ConfirmAccountView(UpdateView):
    form_class = ConfirmAccountForm
    model = User
    template_name = 'user/settings/account.html'

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
        try:
            first_invite_key = InviteKey.objects.filter(invited_user=self.request.user).first()
            return first_invite_key.next

        except AttributeError:
            # was no invite key
            return reverse_lazy('public:home')


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
