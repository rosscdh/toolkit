# -*- coding: utf-8 -*-
from django.conf import settings

import logging
logger = logging.getLogger('django.request')

ENABLE_CELERY_TASKS = getattr(settings, 'ENABLE_CELERY_TASKS', False)


def run_task(task, **kwargs):
    """
    Function to attemt to run a task async, able to revert to running sync
    if exception happens
    """
    skip_async = kwargs.pop('skip_async', False)
    logger.debug('run_task Celery skip_async: %s' % skip_async)

    if ENABLE_CELERY_TASKS is True and skip_async is False:
        try:
            logger.debug('settings.ENABLE_CELERY_TASKS is True, attempting celery')
            task.delay(**kwargs)
            return True

        except Exception as e:
            logger.critical('Could not run task async: %s due to: %s' % (task, e))
    #
    # Run the task sync if specified
    # if fallback is true and celery tasks is disabled still run the task
    #
    if ENABLE_CELERY_TASKS is False or skip_async is True:
        logger.info('Did not run task async: %s now performing synchronously' % task)

        kwargs.pop('countdown', None)  # remove this reserved celery kwarg

        task(**kwargs)
        return True