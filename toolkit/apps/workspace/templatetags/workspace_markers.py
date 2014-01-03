from django import template


register = template.Library()


@register.inclusion_tag('partials/action_button.html')
def action_button(marker, css_class='btn'):
    return {
        'css_class': css_class,
        'marker': marker
    }
