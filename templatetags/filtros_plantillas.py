from django import template

register = template.Library()


def nonep(value):
    if value == None:
        value='-'
    return value

register.filter("nonep",nonep)

@register.filter()
def estado(value):
    if value == True:
        value='Activo'
    else:
        value='Desactivado'
    return value

@register.filter()
def estadosino(value):
    if value == True:
        value='Si'
    else:
        value='No'
    return value


@register.filter()
def numberhtml(value):
    value = str(value)
    value.replace(',','.')

    return value

