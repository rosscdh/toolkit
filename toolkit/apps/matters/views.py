from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from toolkit.api.serializers import LiteMatterSerializer
from toolkit.apps.workspace.models import Workspace
from toolkit.mixins import AjaxModelFormView, ModalView

from .forms import MatterForm


class MatterListView(ListView):
    serializer_class = LiteMatterSerializer
    template_name = 'matters/matter_list.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MatterListView, self).get_context_data(**kwargs)

        context.update({
            'can_create': self.request.user.profile.is_lawyer,
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
        context = self.get_serializer_context()
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
        if settings.DEBUG:
            return 'index.html'
        else:
            return 'dist/index.html'


class MatterCreateView(ModalView, AjaxModelFormView, CreateView):
    form_class = MatterForm

    def get_form_kwargs(self):
        kwargs = super(MatterCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(MatterCreateView, self).form_valid(form)
        messages.success(self.request, 'You have sucessfully created a new matter')
        return response

    def get_success_url(self):
        return reverse('matter:detail', kwargs={'matter_slug': self.object.slug})


class MatterUpdateView(ModalView, AjaxModelFormView, UpdateView):
    form_class = MatterForm
    model = Workspace
    slug_url_kwarg = 'matter_slug'

    def get_form_kwargs(self):
        kwargs = super(MatterUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(MatterUpdateView, self).form_valid(form)
        messages.success(self.request, 'You have sucessfully updated the matter')
        return response

    def get_success_url(self):
        return reverse('matter:detail', kwargs={'matter_slug': self.object.slug})
