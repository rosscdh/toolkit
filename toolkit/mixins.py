from django.forms.forms import BaseForm

from crispy_forms.layout import ButtonHolder, Div, HTML, Layout, Submit


class FormModal(BaseForm):
    def __init__(self, *args, **kwargs):
        super(FormModal, self).__init__(*args, **kwargs)

        self.helper.attrs = {
            'parsley-validate': '',
            'parsley-error-container': '.parsley-errors'
        }
        self.helper.form_show_errors = False

        form_layout = self.helper.layout

        self.helper.layout = Layout(
            Div(
                HTML('<div class="dialog dialog-danger form-errors hide"><div class="container"><p></p><div class="parsley-errors"></div></div></div>'),
                form_layout,
                css_class='modal-body'
            ),
            ButtonHolder(
                HTML('<a href="#" class="btn btn-default btn-wide" data-dismiss="modal">Cancel</a>'),
                Submit('submit', 'Submit', css_class='btn-wide'),
                css_class='modal-footer'
            )
        )
