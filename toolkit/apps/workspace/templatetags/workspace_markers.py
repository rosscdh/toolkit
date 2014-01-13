from django import template


register = template.Library()

ICON_TYPES = {
    "done": 'fui-check-inverted',
    "pending": 'fui-radio-unchecked',
    "next": 'fui-alert',
}

ACTION_BUTTON_CSS_TYPES = {
    "done": 'btn btn-success',
    "pending": 'btn btn-hg btn-info',
    "next": 'btn btn-hg btn-info',
}

@register.inclusion_tag('partials/marker_status_block.html', takes_context=False)
def marker_status_block(marker, user):
    # if the user is of the class required
    try:
        show_action_button = marker.can_perform_action(user=user)
    except NotImplementedError as e:
        show_action_button = False

    # is our current status done then show_complete
    show_complete = marker.status == 'done'

    return {
        'marker': marker,
        'icon_type': ICON_TYPES[marker.status],
        'show_action_button': show_action_button,
        'action_button_css_class': ACTION_BUTTON_CSS_TYPES[marker.status],
        'description_col_css': 'col-md-7' if show_complete is True else 'col-md-11',
        'show_complete': show_complete,
    }


@register.inclusion_tag('partials/action_button.html')
def action_button(marker, css_class='btn'):
    return {
        'css_class': css_class,
        'marker': marker
    }
