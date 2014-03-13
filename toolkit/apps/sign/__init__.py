# -*- coding: utf-8 -*-
from django.conf import settings

from toolkit.utils import get_namedtuple_choices
SIGNER_ASSOCIATION_STRATEGIES = get_namedtuple_choices('SIGNER_ASSOCIATION_STRATEGIES', (
                                                    ('single', 'single', 'Single Signer per SignDocument'),
                                                    ('multi', 'multi', 'Multiple Signers per SignDocument'),
                                                ))

SIGNER_DOCUMENT_ASSOCIATION_STRATEGY = getattr(settings, 'SIGNER_DOCUMENT_ASSOCIATION_STRATEGY', SIGNER_ASSOCIATION_STRATEGIES.single)