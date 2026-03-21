import datetime

import pytz
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import AimDealer, Project, Scrape, SpiderLog, TargetSite, Webprovider
from .utils import ScrapeEntryCode

# Register your models here.


class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
    )


class AimDealerAdminView(admin.ModelAdmin):
    list_max_show_all = 500
    list_per_page = 10
    list_filter = ['account', 'web_provider', 'account_manager']
    list_display_links = ('dealer_id', 'dealer_name')
    ordering = ('dealer_name',)

    list_display = (
        'account_icon',
        'account_status',
        'dealer_id',
        'dealer_name',
        'show_site_url',
        'web_provider',
        'account_manager',
        'date_created_fmt',
        'date_modified_fmt',
    )
    search_fields = [
        'account',
        'dealer_id',
        'dealer_name',
        'site_url',
        'web_provider__name',
        'account_manager',
    ]

    # show vdp urls links
    @admin.display(
        description='VDP URLS', ordering='site_url'
    )  # description is  the column name
    def show_site_url(self, obj):
        if obj.site_url:
            return format_html(
                "<a href='{url}' target='_blank'>{url}</a>", url=obj.site_url
            )
        else:
            return ''

    # function to change the icons
    def account_icon(self, obj):
     if obj.account == 'ACTIVE':
        return True
     elif obj.account == 'INACTIVE':
        return None
     else:
        return False

    account_icon.boolean = True

    # function to color the account status text
    @admin.display(
        description='Status',
        ordering='account',
    )
    def account_status(self, obj):
        if obj.account == 'ACTIVE':
            color = '#28a745'
        elif obj.account == 'INACTIVE':
            color = '#fea95e'
        else:
            color = '#ff0000'
        return format_html('<strong><p style="color:{}">{}</p></strong>',color,obj.account)

    # account_status.allow_tags = True

    # format date
    @admin.display(ordering='date_created')
    def date_created_fmt(self, obj):
        return obj.date_created.strftime("%Y-%m-%d")

    date_created_fmt.short_description = 'Date Created'

    # format date
    @admin.display(ordering='date_modified')
    def date_modified_fmt(self, obj):
        return obj.date_modified.strftime("%Y-%m-%d")

    date_modified_fmt.short_description = 'Date Modified'

    # auto change 'web_provider' field at TargetSite after saving
    # wrap it in `try...except` to get rid of error 'self.model.DoesNotExist'
    def save_model(self, request, obj, form, change):
        try:
            object = TargetSite.objects.get(site_name__dealer_id=obj.dealer_id)
            object.web_provider = obj.web_provider.name
            object.spider = obj.web_provider.name
            object.save()
        except TargetSite.DoesNotExist:
            pass

        # If the entry is being modified, set the modified_by field
        if change:
            obj.modified_by = request.user

        # If the entry is being added, set the author field
        else:
            obj.author = request.user

        # Save the object with the user information
        super().save_model(request, obj, form, change)


class TargetSiteAdminView(admin.ModelAdmin, ScrapeEntryCode):
    # list_per_page = 10
    list_filter = ['site_name__account', 'status', 'web_provider']
    list_display_links = ['target_site_dealer_name']
    ordering = ('-entry_code',)

    list_display = (
        'account_status',
        'scrape_status',
        'entry_code',
        'target_site_dealer_id',
        'target_site_dealer_name',
        'web_provider',
        'show_site_url',
        'feed_id',
        'last_scraped',
        'last_run',
    )
    search_fields = [
        'site_name__account',
        'entry_code',
        'site_name__dealer_id',
        'site_name__dealer_name',
        'status',
        'web_provider',
        'spider',
        'site_url',
        'feed_id',
    ]

    # from `aimdealer.account` via foreign key at `site_name`
    @admin.display(ordering='site_name__account', description='account')
    def account_status(self, obj):
        if obj.site_name.account == 'ACTIVE':
            color = '#28a745'
        elif obj.site_name.account == 'INACTIVE':
            color = '#fea95e'
        else:
            color = '#ff0000'
        return format_html(
        '<strong><span style="color:{}">{}</span></strong>',
        color, 
        obj.site_name.account
        )


    # style at `admin-extra.css`
    @admin.display(ordering='status', description='setup')
    def scrape_status(self, obj):
        # Mapping status to CSS classes defined in admin-extra.css
        status_map = {
            'Active': 'active',
            'Pending': 'pending',
            'Failed': 'failed',
            'Paused': 'paused',
        }
        
        # Get the class from the map, default to 'inactive' if not found
        css_class = status_map.get(obj.status, 'inactive')
        
        # Return safely using placeholders
        return format_html(
            '<span class="status {}">{}</span>',
            css_class,
            obj.status
        )

    account_status.allow_tags = True

    # sorting by `site_name__dealer_id`
    @admin.display(ordering='site_name__dealer_id', description='DID')
    def target_site_dealer_id(self, obj):
        return obj.site_name.dealer_id

    # /admin/project/aimdealer/28738/change/

    @admin.display(ordering='site_name__dealer_name', description='Dealer')
    def target_site_dealer_name(self, obj):
        return obj.site_name.dealer_name

    # allows you to override the default formfield for a foreign keys field
    # in this example, it only sorts the list
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site_name':
            kwargs["queryset"] = AimDealer.objects.order_by('dealer_name')
        return super(TargetSiteAdminView, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    #  Manipulating Data in Django's Admin Panel on Save
    # NOTE: the `obj` is the direct Model's instance being displayed in that row,
    #  but still can access other Model's instance via ForeignKey
    def save_model(self, request, obj, form, change):
        # add `site_url` if it is not yet available or added
        dealer_id = f'{obj.site_name}'.split('-')[0].strip()
        site = AimDealer.objects.get(dealer_id=dealer_id).site_url

        if not obj.site_url:
            obj.site_url = site
            # obj.user = request.user

        # create entry code if not available
        if not obj.entry_code:
            obj.entry_code = self.get_scrape_entry_code(form)

        super().save_model(request, obj, form, change)

    # show vdp urls links
    @admin.display(description='Site Url', ordering='site_url')
    def show_site_url(self, obj):
        return format_html(
            "<a href='{url}' target='_blank'>{url}</a>", url=obj.site_url
        )

    # get total `spider_logs.items_scraped` via foreign key using related_name='spider_logs'
    @admin.display(ordering='spider_logs__items_scraped', description='Last Scraped')
    def last_scraped(self, obj):
        try:
            last_log = obj.spider_logs.last()
            
            if not last_log or last_log.items_scraped is None:
                return mark_safe('<strong style="color:#ff0000" title="Failed to scrape">Error!</strong>')

            did = obj.site_name.dealer_id
            d_name = obj.site_name.dealer_name
            count = last_log.items_scraped

            return format_html(
                '<a href="/admin/project/scrape/?q={did} {name}" target="_blank"><u><strong>{count}</strong></u></a>',
                did=did,
                name=d_name,
                count=count
            )
        except Exception:
            return mark_safe('<strong style="color:#ff0000" title="Failed to scrape">Error!</strong>')

    # get from `scrapes.last_checked` via foreign key using `related_name='scrapes'`
    @admin.display(ordering='scrapes__last_checked', description='Last Run')
    def last_run(self, obj):
        try:
            lr = TargetSite.objects.filter(site_id=obj.site_id).first()
            return lr.scrapes.last().last_checked.strftime("%Y-%m-%d")
        except BaseException:
            return mark_safe(
                '<strong> <p style="color:#ff0000" title="Failed to scrape">Error!</p> </strong>'
            )

    # To avoid duplicating rows values when sorting table at UI
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.distinct()


class DateYesterdayFieldListFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = datetime.datetime.now()  # utc
        tz = pytz.timezone('Asia/Manila')
        date = pytz.utc.localize(today).astimezone(tz)

        yesterday = date - datetime.timedelta(days=1)

        self.links = list(self.links)
        self.links.insert(
            2,
            (
                'since Yesterday',
                {
                    self.lookup_kwarg_since: yesterday,
                    self.lookup_kwarg_until: today,
                },
            ),
        )


class SpiderlogsAdminView(admin.ModelAdmin):
    # list_max_show_all = 500
    # list_per_page = 15
    list_filter = (
        'target_site__web_provider',
        ('date_created', DateYesterdayFieldListFilter),
    )

    ordering = ('-items_scraped', '-date_created')

    list_display_links = ('target_site_dealer_name',)

    list_display = (
        'account_status',
        'target_site_dealer_id',
        'target_site_dealer_name',
        'target_site_site_url',  # via foreignkey
        'spider_name',
        'scraped',
        'elapsed_time',
        'date_created_fmt',
    )
    search_fields = [
        'target_site__site_name__dealer_id',
        'target_site__site_name__dealer_name',
        'target_site__web_provider',
        'spider_name',
        'items_scraped',
        'date_created',
    ]  # date search pattern: YYYY-MM-DD

    @admin.display(ordering='target_site__site_name__account', description='account')
    def account_status(self, obj):
        if obj.target_site.site_name.account == 'ACTIVE':
            color = '#28a745'
        elif obj.target_site.site_name.account == 'INACTIVE':
            color = '#fea95e'
        else:
            color = '#ff0000'
        return format_html(
            '<strong><span style="color:{}">{}</span></strong>',
            color, 
            obj.target_site.site_name.account
        )

    @admin.display(ordering='target_site__site_name__dealer_id', description='DID')
    def target_site_dealer_id(self, obj):
        did = obj.target_site.site_name.dealer_id
        return format_html(
        '<a href="/admin/project/aimdealer/{}/change/" target="_blank"><u>{}</u></a>',
        did,
        did
         )

    @admin.display(ordering='target_site__site_name__dealer_name', description='Dealer')
    def target_site_dealer_name(self, obj):
        return obj.target_site.site_name.dealer_name

    @admin.display()
    def target_site_site_url(self, obj):
        return format_html(
            "<a href='{url}' target='_blank'>{url}</a>", url=obj.target_site.site_url
        )

    @admin.display(ordering='date_created')
    def date_created_fmt(self, obj):
        tz = pytz.timezone('Asia/Manila')
        date = pytz.utc.localize(obj.date_created).astimezone(tz)
        return date.strftime('%Y-%m-%d %I:%M:%S %p')

    @admin.display(ordering='items_scraped')
    def scraped(self, obj):
        items_scraped = obj.items_scraped
        did = (
            obj.target_site.site_name.dealer_id
        )  # access via ForeignKey: Use dot(.) not underscore(_) or dunder(__)
        d_name = obj.target_site.site_name.dealer_name
        if items_scraped:
         return format_html(
                '<a href="/admin/project/scrape/?q={did} {name}" target="_blank"><u><strong>{count}</strong></u></a>',
                did=did,
                name=d_name,
                count=items_scraped
            )
        else:
            return mark_safe('<strong><span style="color:#ff0000">-none-</span></strong>')



class ScrapeAdminView(admin.ModelAdmin):
    list_filter = ['target_site', 'spider']

    list_display = (
        'target_site_dealer_id',
        'target_site_dealer_name',
        'spider',
        'vin',
        'vdp_url',
        'date_created_fmt',
    )
    search_fields = [
        'target_site__site_name__dealer_id',
        'target_site__site_name__dealer_name',
        'spider',
        'stock_number',
        'vin',
        'last_checked',
    ]  # __site_name -- refers to 'site_name' attribute

    list_display_links = ('target_site_dealer_name',)

    @admin.display(ordering='target_site__site_name__dealer_id', description='DID')
    def target_site_dealer_id(self, obj):
        return obj.target_site.site_name.dealer_id

    @admin.display(ordering='target_site__site_name__dealer_name', description='Dealer')
    def target_site_dealer_name(self, obj):
        return obj.target_site.site_name.dealer_name

    @admin.display()
    def vdp_url(self, obj):
        return format_html(
            "<a href='{url}' target='_blank'>{url}</a>", url=obj.vehicle_url
        )

    @admin.display(ordering='date_created')
    def date_created_fmt(self, obj):
        tz = pytz.timezone('Asia/Manila')
        date = pytz.utc.localize(obj.last_checked).astimezone(tz)
        return date.strftime('%Y-%m-%d %I:%M:%S %p')

    date_created_fmt.short_description = 'Date Created'


class WebproviderAdminView(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['id', 'name']
    ordering = ('name',)


# Re-register UserAdmin to customize use display info at admin ui
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Project)
admin.site.register(AimDealer, AimDealerAdminView)
admin.site.register(TargetSite, TargetSiteAdminView)
admin.site.register(Scrape, ScrapeAdminView)
admin.site.register(SpiderLog, SpiderlogsAdminView)
admin.site.register(Webprovider, WebproviderAdminView)


# change back Django Admin header
admin.site.site_header = 'Scrape Bucket Admin'
admin.site.site_title = 'Web Scraping'
admin.site.index_title = 'Admin Console'
