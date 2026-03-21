from django.urls import path

from . import views

app_name = 'project'

urlpatterns = [
    path('', views.get_scraped_items, name='api-scraped-items'),
]
