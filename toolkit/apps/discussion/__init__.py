# -*- coding: utf-8 -*-
from threadedcomments.forms import ThreadedCommentForm

from .models import DiscussionComment


def get_form():
    return ThreadedCommentForm

def get_model():
    return DiscussionComment
