import functools
import heapq
import re
from datetime import datetime

import django.http
from django.http import HttpResponse
from django.urls import register_converter

from .models import Project


class ScrapeEntryCode:
    project_all = Project.objects.all()

    def get_scrape_entry_code(self, form):
        codes = []
        max_num = 1
        for p in self.project_all:
            if form.instance.project.name == p.name:
                for code in self.project_all.filter(name=form.instance.project.name).first().projects.all():
                    take_int = re.findall(r'[A-Za-z]+|\d+', code.entry_code)[-1]
                    codes.append(int(take_int))

        if codes:
            max_num = heapq.nlargest(2, codes)[0] + 1

        proj = form.instance.project.name[:3].upper()
        num = str(max_num).zfill(3)

        return f'{proj}{num}'


def ajax_login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return HttpResponse('<h1> 401 Unauthorized</h1>', status=401)

    return wrapper


class DateConverter:
    regex = '\d{4}-\d{1,2}-\d{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d').date()

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')


register_converter(DateConverter, 'date')


#  select sidebar submenu
def sidebar_submenu_selected(context, project_name):
    selected = {
        'aim-dealers': 'active-underline',
        'vdp-urls': 'active-underline',
        'others': 'active-underline',
    }
    key_name = re.sub('-', '_', project_name)
    context[f'{key_name}_selected'] = selected.get(project_name)
