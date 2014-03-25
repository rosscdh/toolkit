# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver
from django.template.defaultfilters import slugify

from . import _model_slug_exists

import uuid
import logging
import datetime
logger = logging.getLogger('django.request')


#
# Marker Signals
#
""" Primary signal used as wrapper for others """
base_signal = Signal(providing_args=['actor'])


@receiver(base_signal)
def on_base_signal(sender, instance, actor, **kwargs):
    """
    Primary handler that is called and will calculate the current and
    previous instance marker status, and issue the appropriate signals
    """
    markers = instance.markers  # @TODO can refer to instance.markers ?

    # if we are provided a kwargs "name" then use that.. otherwise use the current instance marker
    marker_node = markers.marker(val=kwargs.get('name', instance.status))

    if hasattr(marker_node, 'issue_signals'):
        marker_node.issue_signals(request=sender, instance=instance, actor=actor)
    else:
        logger.error('Requested signal marker "%s" has no issue_signals method' % marker_node)


#
# Update method used to insert data into the instance.data['markers']
#

def _update_marker(marker_name, next_status, actor_name, instance, **kwargs):
    """
    Shared process used by signals to perform status updates
    """
    # get the current marker
    current_marker = instance.markers.marker(marker_name)

    # get the data markers
    markers = instance.data.get('markers', {})
    # capture fields to update
    update_fields = []

    # set our key
    # but only if we dont already have it
    if marker_name not in markers.keys():
        kwargs.update({
            'date_of': datetime.datetime.utcnow(),
            'actor_name': actor_name
        })
        markers[marker_name] = kwargs

        # update markers object @TODO race condition?
        instance.data['markers'] = markers

        update_fields.append('data')

        # set the next status
        # @BUSINESSRULE only update if the current status is less than our reqeusted status
        if instance.status < next_status:
            instance.status = next_status
            update_fields.append('status')

        # save
        instance.save(update_fields=update_fields)

        if hasattr(current_marker, 'on_complete'):
            try:
                current_marker.on_complete()

            except NotImplementedError:
                logger.debug('Marker has no on_complete action: %s for instance: %s' % (marker_name, instance))

#
# End Marker Signals
#

def ensure_workspace_slug(sender, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    workspace = kwargs.get('instance')

    if workspace.slug in [None, '']:

        final_slug = slugify(workspace.name)

        while _model_slug_exists(model=workspace.__class__.objects.model, slug=final_slug):
            logger.info('Workspace %s exists, trying to create another' % final_slug)

            slug = '%s-%s' % (final_slug, uuid.uuid4().get_hex()[:4])
            slug = slug[:30]
            final_slug = slugify(slug)

        workspace.slug = final_slug


def ensure_workspace_matter_code(sender, instance, **kwargs):
    """
    signal to handle creating the workspace matter_code
    instance = workspace
    """

    if instance.matter_code in [None, '']:

        # the current number of matters this lawyer has
        count = instance.lawyer.workspace_set.all().count() if instance.lawyer is not None else 1
        workspace_name = slugify(instance.name)

        final_matter_code = "{0:05d}-{1}".format(count, workspace_name)

        while _model_slug_exists(model=instance.__class__.objects.model, matter_code=final_matter_code):
            logger.info('Workspace %s exists, trying to create another' % final_matter_code)
            count = count + 1
            final_matter_code = "{0:05d}-{1}".format(count, workspace_name)

        instance.matter_code = final_matter_code


def ensure_tool_slug(sender, **kwargs):
    """
    signal to handle creating a new Tool
    """
    tool = kwargs.get('instance')

    if tool.slug in [None, '']:

        final_slug = slugify(tool.name)

        while _model_slug_exists(model=tool.__class__.objects.model.model, slug=final_slug):
            logger.info('Tool %s exists, trying to create another' % final_slug)

            slug = '%s-%s' % (final_slug, uuid.uuid4().get_hex()[:4])
            slug = slug[:30]
            final_slug = slugify(slug)

        tool.slug = final_slug
