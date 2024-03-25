from django import template

register = template.Library()

@register.filter(name='hours')
def hours(value):
    return f'{value.seconds // 3600:02d}'

@register.filter(name='minutes')
def minutes(value):
    return f'{(value.seconds % 3600) // 60:02d}'

@register.filter(name='seconds')
def seconds(value):
    return f'{value.seconds % 60:02d}'