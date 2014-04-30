# -*- coding: utf-8 -*-
from django.template.loader import get_template

#
# Delivered here to make accessable to multiple serializers
#
ACTIVITY_TEMPLATES = {
    'default': get_template('activity/default.html'),
    'item-commented': get_template('activity/item_comment.html'),
    'revision-added-review-session-comment': get_template('activity/review_session_comment.html'),
    'revision-added-revision-comment': get_template('activity/revision_comment.html'),
}

NOTIFICATION_TEMPLATES = {
    'default': get_template('notification/partials/default.html'),
    'item-commented': get_template('notification/partials/item_comment.html'),
    'revision-added-review-session-comment': get_template('notification/partials/review_session_comment.html'),
    'revision-added-revision-comment': get_template('notification/partials/revision_comment.html'),
}