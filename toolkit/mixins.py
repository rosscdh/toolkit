from django.forms.forms import BaseForm
from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.generic.base import View
from django.views.generic.edit import FormView

from crispy_forms.layout import ButtonHolder, Div, HTML, Layout, Submit

from .decorators import json_response


class JSONResponseMixin(object):
    def render_to_json_response(self, context, **kwargs):
        return self.get_json_response(self.convert_context_to_json(context), **kwargs)

    def get_json_response(self, content, **kwargs):
        return HttpResponse(content, content_type='application/json', **kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)


class AjaxFormViewMixin(object):
    """
    A mixin that handles form submission over AJAX.
    """
    @json_response
    def post(self, request, *args, **kwargs):
        return super(AjaxFormViewMixin, self).post(request)

    @json_response
    def put(self, request, *args, **kwargs):
        return super(AjaxFormViewMixin, self).put(request)


class AjaxValidFormViewMixin(JSONResponseMixin, AjaxFormViewMixin):
    """
    A mixin that handles successful AJAX form submissions for simple
    FormView based views.
    """
    def form_valid(self, form):
        data = {
            'redirect': True,
            'url': self.get_success_url()
        }

        return self.render_to_json_response(data)


class AjaxValidModelFormViewMixin(JSONResponseMixin, AjaxFormViewMixin):
    """
    A mixin that handles successful AJAX form submissions for views
    that use a Django ModelForm.
    """
    def form_valid(self, form):
        self.object = form.save()

        data = {
            'redirect': True,
            'url': self.get_success_url()
        }

        return self.render_to_json_response(data)


class AjaxInvalidFormViewMixin(JSONResponseMixin, AjaxFormViewMixin):
    """
    A mixin that handles invalid AJAX form submissions for FormView based views.
    """
    def form_invalid(self, form):
        errors = form.errors['__all__'] if '__all__' in form.errors else form.errors
        data = {
            'errors': errors
        }
        return self.render_to_json_response(data, status=400)


class AjaxFormView(AjaxValidFormViewMixin, AjaxInvalidFormViewMixin, FormView):
    """
    A mixin that handles AJAX form submissions for FormView based views.

    See: https://docs.djangoproject.com/en/1.6/topics/class-based-views/generic-editing/#basic-forms
    """
    pass


class AjaxModelFormView(AjaxValidModelFormViewMixin, AjaxInvalidFormViewMixin, FormView):
    """
    A mixin that handles AJAX form submissions for views that use a ModelForm.

    See: https://docs.djangoproject.com/en/1.6/topics/class-based-views/generic-editing/#model-forms
    """
    pass


class ModalForm(BaseForm):
    """
    A mixin that sets up a Form to be displayed in a modal dialog.
    """
    def __init__(self, *args, **kwargs):
        super(ModalForm, self).__init__(*args, **kwargs)

        self.helper.attrs = {
            'data-remote': 'true',
            'parsley-validate': ''
        }
        self.helper.form_show_errors = False

        form_layout = self.helper.layout

        self.helper.layout = Layout(
            Div(
                HTML('{% include "partials/form-errors.html" with form=form %}'),
                form_layout,
                css_class='modal-body'
            ),
            ButtonHolder(
                HTML('<a href="#" class="btn btn-default btn-wide" data-dismiss="modal">Cancel</a>'),
                Submit('submit', 'Submit', css_class='btn-wide'),
                css_class='modal-footer'
            )
        )


class ModalView(View):
    """
    A mixin that sets the correct template for modal based views.
    """
    template_name = 'modal.html'
