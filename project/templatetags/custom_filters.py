from datetime import datetime

from django import template

register = template.Library()

import re

from django.utils import timezone as tz
from rest_framework.authtoken.models import Token


# 1st in a sequence
@register.filter(name='str_split')
def str_split(value, arg):
    return value.split(arg)


# 2nd in a sequence
@register.filter(name='str_join')
def str_join(value, arg):
    return arg.join(value)


@register.filter(name='str_upper')
def str_upper(value, arg):
    return re.sub(arg, arg.upper(), value)


@register.filter(name='replace_if_empty')
def replace_if_empty(value, arg):
    if not value or value == '':
        value = arg
    return value


@register.filter(name='get_field_values')
def get_field_values(value, arg):
    values = value.values_list(arg, flat=True).distinct()
    uniq_values = sorted(list(set(values)))  # returns a unique data queryset --> Model.objects.values_list('last_checked', flat=True).distinct()
    return uniq_values


@register.filter(name='convert_str_date')
def convert_str_date(value):
    if value:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
    # format: 2022-04-02 01:14:19.176758 --> datetime.datetime(2022, 4, 2, 1, 14, 19, 176758)


@register.filter
def to_str(value):
    return str(value)


@register.filter(name='sort_queryset')
def sort_queryset(value, arg):
    return value.order_by(arg)


@register.filter(name='get_api_authtoken')
def get_api_authtoken(value):
    try:
        token = Token.objects.get(user=value)
        return token.key
    except Token.DoesNotExist as err:
        return f'{err} Please contact admin.'
