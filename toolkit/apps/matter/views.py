from django.conf import settings
from django.core import signing
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView, View

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from toolkit.api.serializers import LiteMatterSerializer
from toolkit.apps.matter.services import (MatterRemovalService, MatterParticipantRemovalService)
from toolkit.apps.workspace.models import Workspace, ExportedMatter
from toolkit.mixins import AjaxModelFormView, ModalView

from rest_framework.renderers import UnicodeJSONRenderer

from .forms import MatterForm

import logging
logger = logging.getLogger('django.request')


class MatterDownloadExportView(View):
    def get(self, request, *args, **kwargs):
        exported_matter_id = signing.loads(kwargs.get('token'), salt=settings.SECRET_KEY)
        exported_matter = ExportedMatter.objects.get(id=exported_matter_id)

        fsock = file.open(exported_matter.file, "rb")
        response = HttpResponse(fsock, mimetype='application/zip')
        return response


class MatterListView(ListView):
    serializer_class = LiteMatterSerializer
    template_name = 'matter/matter_list.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MatterListView, self).get_context_data(**kwargs)

        object_list = self.get_serializer(self.object_list, many=True).data

        context.update({
            'can_create': self.request.user.profile.is_lawyer,
            'can_delete': self.request.user.profile.is_lawyer,
            'can_edit': self.request.user.profile.is_lawyer,
            #'object_list': object_list,
            'object_list_json': UnicodeJSONRenderer().render(object_list),
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

        if self.object.lawyer == request.user:
            service = MatterRemovalService(matter=self.object, removing_user=request.user)
            service.process()

        else:
            #
            # Is a participant trying to stop participating
            #
            service = MatterParticipantRemovalService(matter=self.object, removing_user=request.user)
            service.process(user_to_remove=request.user)

        return HttpResponseRedirect(success_url)
