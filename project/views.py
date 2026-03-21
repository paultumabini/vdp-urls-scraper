import csv
import re
from datetime import datetime, timedelta, timezone
from ftplib import FTP
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import IntegerField, Q, Sum
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import SiteCreateForm
from .models import AimDealer, Project, Scrape, SpiderLog, TargetSite, Webprovider
from .utils import ScrapeEntryCode, ajax_login_required, sidebar_submenu_selected


@login_required
def home(request):
    total = (
        SpiderLog.objects.annotate(as_int=Cast('items_scraped', IntegerField()))
        .aggregate(Sum('as_int'))
        .get('as_int__sum')
        if SpiderLog.objects
        else 0
    )

    context = {
        'active_highlight': 'active-highlight',
        'dropdown_arrow': 'down',
        'project': Project.objects.all(),
        'provider': TargetSite.objects,
        'total_scrapes': (
            f'{total:,}' if total else None
        ),  # '{:,}' ⟶ comma separated number, i.e,  1234567 ⟶ 1,234,567
    }

    return render(request, 'project/home.html', context)


class SiteListView(LoginRequiredMixin, ListView):
    template_name = 'project/targetsites.html'
    context_object_name = 'sites'
    ordering = ['-date_created']
    extra_context = {  # or 'get_context_data' method below
        'aim_highlight': 'active-highlight',
        'dropdown': 'show',
        'dropdown_arrow': 'up',
        'scrapes': Scrape.objects.all(),
    }

    # filter project key passed in the url to get the specific project
    def get_queryset(self):
        self.project = get_object_or_404(Project, name=self.kwargs.get('project_name'))
        return (
            Project.objects.filter(name=self.project)
            .first()
            .projects.all()
            .order_by('-date_created')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # set css for selected submenu
        sidebar_submenu_selected(context, self.project.name)

        # section label
        context['project'] = self.project.name
        return context


class SiteDetailView(LoginRequiredMixin, DetailView):
    model = TargetSite
    extra_context = {
        'dropdown_arrow': 'up',
        'aim_highlight': 'active-highlight',
        'submenu': 'show',
    }

    context_object_name = 'sites'  # or just use {{object.<property>}} in the template

    # set additional context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_name = (
            TargetSite.objects.filter(site_id=self.kwargs.get('pk'))
            .first()
            .project.name
        )

        # set css for selected submenu
        sidebar_submenu_selected(context, project_name)

        # context['form'] = SiteCreateForm
        return context


class SiteCreateView(LoginRequiredMixin, CreateView, ScrapeEntryCode):
    model = TargetSite
    form_class = SiteCreateForm

    extra_context = {
        'dropdown_arrow': 'down',
        'projects': Project.objects.all(),
        'object': Project,
    }

    #  sort `site_name` dropdown options on template
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['site_name'].queryset = AimDealer.objects.order_by('dealer_name')
        return form

    def form_valid(self, form):
        #  restrict 'test user'
        if str(self.request.user) == 'testuser':
            messages.add_message(
                self.request,
                messages.WARNING,
                'This user is not authorized to submit this request. Please ask for assistance.',
                extra_tags='exclamation',
            )
            return redirect('new-scrape')

        form.instance.author = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.entry_code = self.get_scrape_entry_code(form)

        # save new site provider and spider
        provider = ''.join(
            [wp.lower() for wp in form.cleaned_data.get('web_provider').split(' ')]
        )
        form.instance.web_provider = provider
        form.instance.spider = provider

        # create new web provider
        if not Webprovider.objects.filter(name__iexact=provider).first():
            Webprovider.objects.create(name=provider)

        messages.success(
            self.request,
            f' Scrape request for \'{form.cleaned_data.get("site_name")}\' has been successfully submitted.',
            extra_tags='check',
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        form['site_name'].field.widget.attrs.update({'class': ''})
        return super().form_invalid(form)

    # if not log in and trying to access this route:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # messages.add_message(request, messages.WARNING, ' Please log in to have access to this page', extra_tags='text-center')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class SiteUpdateView(LoginRequiredMixin, UpdateView, ScrapeEntryCode):
    model = TargetSite
    form_class = SiteCreateForm

    extra_context = {
        'dropdown_arrow': 'down',
        'projects': Project.objects.all(),
        'object': Project,
    }

    #  sort `site_name` dropdown options on template
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['site_name'].queryset = AimDealer.objects.order_by('dealer_name')
        return form

    def form_valid(self, form):
        #  restrict 'test user'
        if str(self.request.user) == 'testuser':
            messages.add_message(
                self.request,
                messages.WARNING,
                f'This user is not authorized to submit this request. Please ask for assistance.',
                extra_tags='exclamation',
            )
            return redirect('update-scrape', pk=self.kwargs.get('pk'))

        form.instance.updated_by = self.request.user

        # update new site provider and spider
        provider = ''.join(
            [wp.lower() for wp in form.cleaned_data.get('web_provider').split(' ')]
        )
        form.instance.web_provider = provider
        form.instance.spider = provider

        if not Webprovider.objects.filter(name__iexact=provider).first():
            Webprovider.objects.create(name=provider)

        messages.success(
            self.request,
            f'  \'{form.cleaned_data.get("site_name")}\' info has been successfully updated.',
            extra_tags='check',
        )

        return super().form_valid(form)


#  CBV delete view
class SiteDeleteView(LoginRequiredMixin, DeleteView):
    model = TargetSite

    def dispatch(self, request, *args, **kwargs):
        site = self.get_object()
        # restrict 'test user'
        if not self.request.user.is_superuser:
            messages.warning(
                request,
                f'You are not authorized to execute this request. Please ask for assistance',
                extra_tags='exclamation',
            )
            if self.kwargs.get('page') == 'dealer-list':
                return redirect('site-list', project=site.project)
            else:
                return redirect('site-detail', pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request,
            f'Successfully deleted: { self.object.site_name} ',
            extra_tags='check',
        )
        return reverse('site-list', kwargs={'project_name': self.object.project})


#  function based delete view
@login_required
def delete_site(request, pk):

    site = TargetSite.objects.filter(site_id=pk).first()

    if request.method == 'POST' and request.user.is_superuser:
        site.delete()
        messages.success(
            request, f'Successfully deleted: {site.site_name} ', extra_tags='check'
        )
        return redirect('site-list', project=site.project)
    else:
        messages.warning(
            request,
            f'Sorry, you\'re not authorized to execute this request',
            extra_tags='exclamation',
        )
        return redirect('site-list', project=site.project)


@login_required
def api_docs(request):
    context = {
        'title': 'Api Docs',
        'api_guide_highlight': 'active-highlight',
        'dropdown_arrow': 'down',
    }
    return render(request, 'project/api_docs.html', context)


@login_required
def help(request):
    context = {
        'title': 'Help',
        'help_highlight': 'active-highlight',
        'dropdown_arrow': 'down',
    }
    return render(request, 'project/help.html', context)


# json data
@ajax_login_required
def scrape_data_json(request):

    # scrapes = Scrape.objects.filter(last_checked__lt=datetime.now(timezone.utc) - timedelta(hours=5)) # __lt = lessthan
    # scrapes = Scrape.objects.filter(last_checked__gte=datetime.now() - timedelta(days=1)) # __gte = greater than or equal

    response = list(Scrape.objects.values())
    return JsonResponse(response, safe=False)


@ajax_login_required
def spider_logs_json(request):
    response = list(SpiderLog.objects.values())
    return JsonResponse(response, safe=False)


@ajax_login_required
def web_providers_json(request):
    response = list(Webprovider.objects.values())
    return JsonResponse(response, safe=False)


@ajax_login_required
def aim_dealers_list(request):
    response = list(AimDealer.objects.values())
    return JsonResponse(response, safe=False)


def scrape_data_csv(request, project_name):
    id = request.GET.get('target_id')  # domain_name as `pk`

    checkboxes = {
        'condition': 'condition',
        'unit': 'unit',
        'year': 'year',
        'make': 'make',
        'model': 'model',
        'trim': 'trim',
        'stock_number': 'stock_number',
        'vin': 'vin',
        'vehicle_url': 'vehicle_url',
        'msrp': 'msrp',
        'price': 'price',
        'selling_price': 'selling_price',
        'rebate': 'rebate',
        'discount': 'discount',
        'images': 'image_urls',
        'images_count': 'images_count',
    }

    try:
        scrapes = TargetSite.objects.filter(site_id=id).first().scrapes.all()
        scrape_date = scrapes.first().last_checked.strftime("%Y-%m-%d")

        checkbox_selected = []

        for k, v in checkboxes.items():
            obj = (
                TargetSite.objects.filter(**{k: True}).all().filter(site_id=id).first()
            )
            if obj:
                checkbox_selected.append(v)
        items_filtered = []

        for item in scrapes.values():
            filtered = {}
            for checkbox in checkbox_selected:
                filtered[checkbox] = item.get(checkbox)
            items_filtered.append(filtered)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment;filename={id}_scraped_{scrape_date}.csv'
        )

        writer = csv.writer(response)

        field_names = items_filtered[0].keys()
        writer.writerow(field_names)

        for item in items_filtered:
            writer.writerow([value for value in item.values()])

        #  return response to download csv on local machine
        return response

    except Exception as e:
        print('Error Msg: ', e)
        messages.warning(
            request,
            ' No available data to download. Please check site details below or contact Paul!',
            extra_tags='exclamation',
        )

        return redirect('site-detail', pk=id, project_name=project_name)


# testing api using a regular JsonResponse & HttpResponse
def test_api(request):
    try:
        provider = request.GET.get('webprovider', False)
        target_site = request.GET.get('domains', False)

        if 'webprovider' and 'domains' in request.GET and target_site == 'all':
            scrapes = Scrape.objects.filter(spider=provider).all()
            if scrapes:
                response = list(scrapes.values())
                return JsonResponse({provider: response}, safe=False)
            else:
                return HttpResponse('<h1>SEARCH NOT FOUND</h1>')
        else:
            scrapes = Scrape.objects.filter(
                spider=provider, target_site_id=target_site
            ).all()
            if scrapes:
                response = list(scrapes.values())
                return JsonResponse({provider: response}, safe=False)
            else:
                return HttpResponse('<h1>SEARCH NOT FOUND</h1>')
    except Exception as e:
        print('Error Msg: ', e)
        return HttpResponse('<h1>Invalid search query</h1>')
