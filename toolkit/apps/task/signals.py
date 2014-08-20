# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('django.request')


def _update_task_count(item):
    complete, total = 0, 0
    #
    # Dont use .count() here as we want a single instance to be returned
    #
    for task in item.task_set.all().values('is_complete'):
        total += 1
        if task.get('is_complete', False) is True:
            complete += 1

    logger.debug('item %s has %d/%d completed tasks' % (item.slug, complete, total))

    data = item.data
    tasks = data.get('tasks', {'complete': complete, 'total': total})
    tasks.update({
        'complete': complete,
        'total': total,
    })
    data.update({'tasks': tasks})
    item.data = data
    item.save(update_fields=['data'])


def _update_participants_requests_count(task):
    for user in task.item.matter.participants.all():
        profile = user.profile
        profile.open_requests = profile.get_open_requests_count()
        profile.save(update_fields=['data'])


def post_save_update_task_complete_count_in_item(sender, instance, **kwargs):
    _update_task_count(item=instance.item)

    if kwargs.get('created', False) is True:
        instance.item.matter.actions.added_task(user=instance.created_by, item=instance.item, task=instance)

    _update_participants_requests_count(task=instance)


def post_delete_update_task_complete_count_in_item(sender, instance, **kwargs):
    _update_task_count(item=instance.item)
    _update_participants_requests_count(task=instance)