from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse, reverse_lazy


class Project(models.Model):
    name = models.CharField(max_length=50, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    # author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.name)


class Webprovider(models.Model):
    name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f'{self.name}' or ''


class AimDealer(models.Model):
    ACCOUNT_STATUS = (
        ('ACTIVE', 'ACTIVE'),
        ('INACTIVE', 'INACTIVE'),
        ('DELETED', 'DELETED'),
    )

    account = models.CharField(max_length=10, choices=ACCOUNT_STATUS)
    dealer_id = models.IntegerField(primary_key=True)
    dealer_name = models.CharField(max_length=200, null=True)
    site_url = models.CharField(max_length=200, null=True)
    web_provider = models.ForeignKey(
        Webprovider, on_delete=models.SET_NULL, related_name='web_provider', null=True, blank=True
    )
    account_manager = models.CharField(max_length=50, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='author', null=True, blank=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='modified_by', null=True, blank=True)

    def __str__(self):
        return f'{self.dealer_id} - {self.dealer_name}'


class TargetSite(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
        ('Paused', 'Paused'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    entry_code = models.CharField(max_length=20, blank=True, default='', verbose_name='entry#')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='projects', null=True)
    site_id = models.CharField(max_length=50, primary_key=True, verbose_name='site id (domain)')  # domain_name input
    site_name = models.ForeignKey(AimDealer, on_delete=models.CASCADE, null=True)
    site_url = models.CharField(max_length=200, blank=True, null=True)
    web_provider = models.CharField(max_length=50, blank=True, null=True)
    feed_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='feed#')
    spider = models.CharField(max_length=50, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sites', null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_by', null=True)
    note = models.TextField(blank=True, null=True)
    condition = models.BooleanField()
    unit = models.BooleanField()
    year = models.BooleanField()
    make = models.BooleanField()
    model = models.BooleanField()
    trim = models.BooleanField()
    stock_number = models.BooleanField()
    vin = models.BooleanField()
    vehicle_url = models.BooleanField()
    msrp = models.BooleanField()
    price = models.BooleanField()
    selling_price = models.BooleanField()
    rebate = models.BooleanField()
    discount = models.BooleanField()
    images = models.BooleanField()
    images_count = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.site_name) or ''

    #  reverse return the full url as a string for creating site view or use  get_success_url(self) at CBV
    def get_absolute_url(self):
        """must follow and return the set url pattern i,e :
        project/<project_name>/<str:pk>/

        reverse(*args,**kwargs) is same as reverse_lazy(*args,**kwargs). Example:
            reverse_lazy('site-detail', kwargs={'project_name': self.project, 'pk': self.pk})
        """
        return reverse('site-detail', kwargs={'project_name': self.project, 'pk': self.pk})

    # def save(self, force_insert=False, force_update=False):
    #     self.entry_code = ''
    #     existing_entry_code = TargetSite.objects.all().order_by('-entry_code')
    #     if existing_entry_code.count() > 0:

    #         new_entry_code = int(existing_entry_code.count()) + 1
    #     else:
    #         new_entry_code = 1
    #     self.entry_code = f'SB-{new_entry_code}'
    #     super().save(force_insert, force_update)


class Scrape(models.Model):
    spider = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    unit = models.CharField(max_length=200, null=True, blank=True)
    year = models.CharField(max_length=10, null=True, blank=True)
    make = models.CharField(max_length=50, null=True, blank=True)
    model = models.CharField(max_length=200, null=True, blank=True)
    trim = models.CharField(max_length=200, null=True, blank=True)
    stock_number = models.CharField(max_length=50, null=True, blank=True)
    vin = models.CharField(max_length=50, null=True, blank=True)
    vehicle_url = models.CharField(max_length=255, null=True, blank=True)
    msrp = models.CharField(max_length=50, null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    selling_price = models.CharField(max_length=50, null=True, blank=True)
    rebate = models.CharField(max_length=50, null=True, blank=True)
    discount = models.CharField(max_length=50, null=True, blank=True)
    image_urls = models.TextField(null=True, blank=True)
    images_count = models.CharField(max_length=50, null=True, blank=True)
    page = models.CharField(max_length=50, null=True, blank=True)
    last_checked = models.DateTimeField(auto_now_add=True, null=True)
    target_site = models.ForeignKey(TargetSite, on_delete=models.CASCADE, related_name='scrapes', null=True)

    def __str__(self):
        return f'{self.target_site} - stk: {self.stock_number} - {self.last_checked.strftime("%Y-%m-%d %I:%M:%S %p")}'


class SpiderLog(models.Model):
    spider_name = models.CharField(max_length=50, null=True)
    allowed_domain = models.CharField(max_length=50, null=True)
    items_scraped = models.CharField(max_length=50, null=True)
    items_dropped = models.CharField(max_length=50, null=True)
    finish_reason = models.CharField(max_length=50, null=True)
    request_count = models.CharField(max_length=50, null=True)
    status_count_200 = models.CharField(max_length=50, null=True)
    start_timestamp = models.CharField(max_length=50, null=True)
    end_timestamp = models.CharField(max_length=50, null=True)
    elapsed_time = models.CharField(max_length=50, null=True)
    elapsed_time_seconds = models.CharField(max_length=50, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    target_site = models.ForeignKey(TargetSite, on_delete=models.CASCADE, related_name='spider_logs')

    def __str__(self):
        return f'{str(self.target_site)} - {self.items_scraped} | {self.date_created.strftime("%Y-%m-%d %I:%M:%S %p")}'
