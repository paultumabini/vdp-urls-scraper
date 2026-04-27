from datetime import datetime
import re

from django import template
from django.utils import timezone as tz
from rest_framework.authtoken.models import Token

register = template.Library()


@register.filter(name='str_split')
def str_split(value, arg):
    return value.split(arg)


@register.filter(name='str_join')
def str_join(value, arg):
    return arg.join(value)


@register.filter(name='str_upper')
def str_upper(value, arg):
    return re.sub(arg, arg.upper(), value)


@register.filter(name='replace_if_empty')
def replace_if_empty(value, arg):
    return arg if not value else value


@register.filter(name='get_field_values')
def get_field_values(value, arg):
    values = value.values_list(arg, flat=True).distinct()
    # Return deterministic unique values for template iteration.
    return sorted(set(values))


@register.filter(name='convert_str_date')
def convert_str_date(value):
    if value:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')


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
    except Token.DoesNotExist:
        return 'Auth token not found. Please contact admin.'
