from django.forms.forms import BaseForm
from django.views.generic.base import View

from crispy_forms.layout import ButtonHolder, Div, HTML, Layout, Submit


class ModalForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(ModalForm, self).__init__(*args, **kwargs)

        self.helper.attrs = {
            'parsley-validate': '',
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
