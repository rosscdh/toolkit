# -*- coding: utf-8 -*-


def _model_slug_exists(model, queryset=None, **kwargs):
    #
    # allow override of queryset
    #
    queryset = model.objects if queryset is None else queryset
    try:
        return queryset.get(**kwargs)
    except model.DoesNotExist:
        return None
