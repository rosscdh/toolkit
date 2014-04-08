from django.conf import settings

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from toolkit.api.serializers import LiteMatterSerializer
from toolkit.apps.workspace.models import Workspace
from toolkit.mixins import AjaxModelFormView, ModalView

from .forms import MatterForm


class MatterListView(ListView):
    serializer_class = LiteMatterSerializer
    template_name = 'matter/matter_list.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user).filter(is_archived=False)

    def get_context_data(self, **kwargs):
        context = super(MatterListView, self).get_context_data(**kwargs)

        context.update({
            'can_archive': self.request.user.profile.is_lawyer,
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


class ArchivedMatterListView(MatterListView):
    template_name = 'matter/matter_list_archived.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user).filter(is_archived=True)


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


class MatterArchiveView(ModalView, DetailView):
    model = Workspace
    slug_url_kwarg = 'matter_slug'
    template_name = 'matter/matter_confirm_archive.html'

    def archive(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.archive()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.archive(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('matter:list')


class MatterUnarchiveView(ModalView, DetailView):
    model = Workspace
    slug_url_kwarg = 'matter_slug'
    template_name = 'matter/matter_confirm_unarchive.html'

    def unarchive(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.archive(is_archived=False)
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.unarchive(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('matter:list')


class MatterDeleteView(ModalView, DeleteView):
    model = Workspace
    slug_url_kwarg = 'matter_slug'
    template_name = 'matter/matter_confirm_delete.html'

    def get_success_url(self):
        return reverse('matter:list')
