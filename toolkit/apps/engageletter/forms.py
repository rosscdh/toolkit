# -*- coding: utf-8 -*-
from parsley.decorators import parsleyfy

from .signals import lawyer_setup_template, lawyer_complete_form, customer_complete_form 

import datetime

import logging
logger = logging.getLogger('django.request')


def _current_year():
    return datetime.datetime.utcnow().year


class BaseForm(WorkspaceToolFormMixin): pass


@parsleyfy
class CustomerForm(BaseForm): pass


@parsleyfy
class LawyerForm(BaseForm): pass