# -*- coding: utf-8 -*-
from django.conf import settings

import logging
logger = logging.getLogger('django.request')

RUN_TASKS = getattr(settings, 'RUN_TASKS', False)
ENABLE_CELERY_TASKS = getattr(settings, 'ENABLE_CELERY_TASKS', False)


def run_task(task, fallback_enabled=True, **kwargs):
    """
    Function to attemt to run a task async, able to revert to running sync
    if exception happens
    """
    if RUN_TASKS is False:
        logger.info('settings.RUN_TASKS is not True')
        return None

    if ENABLE_CELERY_TASKS is True:
        try:
            logger.info('settings.ENABLE_CELERY_TASKS is True, attempting celery')
            task.delay(**kwargs)
            return True

        except Exception as e:
            logger.critical('Could not run task async: %s due to: %s' % (task, e))
    #
    # Run the task sync if specified
    #
    if fallback_enabled is True:
        logger.critical('Could not run task async: %s falling back to synchronously' % task)
        task(user=self.request.user, revision=self.object)
        return True