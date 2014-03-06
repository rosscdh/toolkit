from django import template

register = template.Library()


@register.inclusion_tag('partials/avatar.html', takes_context=False)
def avatar(user):
    return {
        'user': user,
    }
