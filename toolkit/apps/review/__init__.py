# -*- coding: utf-8 -*-
from django.conf import settings

from toolkit.utils import get_namedtuple_choices
REVIEWER_ASSOCIATION_STRATEGIES = get_namedtuple_choices('REVIEWER_ASSOCIATION_STRATEGIES', (
                                                    ('single', 'single', 'Single Reviewer per ReviewDocument'),
                                                    ('multi', 'multi', 'Multiple Reviewer per ReviewDocument'),
                                                ))

REVIEWER_DOCUMENT_ASSOCIATION_STRATEGY = getattr(settings, 'REVIEWER_DOCUMENT_ASSOCIATION_STRATEGY', REVIEWER_ASSOCIATION_STRATEGIES.single)