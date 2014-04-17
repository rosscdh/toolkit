from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from toolkit.api.serializers import LiteMatterSerializer
from toolkit.apps.workspace.models import Workspace
from toolkit.mixins import AjaxModelFormView, ModalView

from .forms import MatterForm

import logging
logger = logging.getLogger('django.request')


class MatterListView(ListView):
    serializer_class = LiteMatterSerializer
    template_name = 'matter/matter_list.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MatterListView, self).get_context_data(**kwargs)

        context.update({
            'can_create': self.request.user.profile.is_lawyer,
            'can_delete': self.request.user.profile.is_lawyer,
            'can_edit': self.request.user.profile.is_lawyer,
            'object_list': self.get_serializer(self.object_list, many=True).data,
        })

        return context

    def get_serializer(self, instance=None, data=None,
                       files=None, many=False, partial=False):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.serializer_class
        self.get_serializer_context()
        return serializer_class(instance)

    def get_serializer_context(self):
        return {
            'request': self.request
        }


class MatterDetailView(TemplateView):
    """
    Just a proxy view through to the AngularJS app.
    """
    def get_template_names(self):
        if settings.PROJECT_ENVIRONMENT in ['prod'] or settings.DEBUG is False:
            return ['dist/index.html']
        else:
            return ['index.html']


class MatterCreateView(ModalView, AjaxModelFormView, CreateView):
    form_class = MatterForm

    @method_decorator(user_passes_test(lambda u: u.profile.validated_email is True, login_url=reverse_lazy('me:email-not-validated')))
    def dispatch(self, *args, **kwargs):
        return super(MatterCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(MatterCreateView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'is_new': True
        })
        return kwargs

    def get_success_url(self):
        return self.object.get_absolute_url()


class MatterUpdateView(ModalView, AjaxModelFormView, UpdateView):
    form_class = MatterForm
    model = Workspace
    slug_url_kwarg = 'matter_slug'

    def get_form_kwargs(self):
        kwargs = super(MatterUpdateView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'is_new': False
        })
        return kwargs

    def get_success_url(self):
        return reverse('matter:list')


class MatterDeleteView(ModalView, DeleteView):
    model = Workspace
    slug_url_kwarg = 'matter_slug'
    template_name = 'matter/matter_confirm_delete.html'

    def get_success_url(self):
        return reverse('matter:list')

    def get_context_data(self, **kwargs):
        context = super(MatterDeleteView, self).get_context_data(**kwargs)
        context.update({
            'action': 'delete' if self.request.user == self.object.lawyer else 'stop-participating'
        })
        return context

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()

        if request.user == self.object.lawyer:
            #
            # Only the lawyer can delete a matter
            #
            self.object.delete()
        else:
            #
            # participants can remove themselves
            #
            if request.user in self.object.participants.all():
                self.object.participants.remove(request.user)
                # send activity event
                self.object.actions.user_stopped_participating(user=request.user)

            else:
                logger.error('User %s tried to delete a matter: %s but was not the lawyer nor the participant' % (request.user, self.object))
                raise PermissionDenied('You are not a participant of this matter')

        return HttpResponseRedirect(success_url)
