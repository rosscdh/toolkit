# -*- coding: utf-8 -*-
from django.views.generic import FormView

from .forms import EightyThreeBForm


class CreateEightyThreeBView(FormView):
    form_class = EightyThreeBForm
    template_name = 'eightythreeb/eightythreeb_form.html'
