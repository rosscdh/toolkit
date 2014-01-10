from django.forms.forms import BaseForm
from django.views.generic.base import View

from crispy_forms.layout import ButtonHolder, Div, HTML, Layout, Submit


class ModalForm(BaseForm):
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
    template_name = 'modal.html'


class AjaxableFormViewResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    and Modal Views
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors = form.errors['__all__'] if '__all__' in form.errors else form.errors
            data = {
                'errors': errors
            }
            return self.render_to_json_response(data, status=400)
        else:
            return super(AjaxableResponseMixin, self).form_invalid(form)

    def form_valid(self, form):
        """ save the form but also render via ajax if ajax request """
        if self.request.is_ajax():
            if hasattr(form, 'instance'):
                form.instance.save()
                data = {
                    'pk': form.instance.pk,
                    'url': form.instance.get_absolute_url() if hasattr(form.instance, 'get_absolute_url') else None,
                }
                return self.render_to_json_response(data)

        return super(AjaxableResponseMixin, self).form_valid(form)
