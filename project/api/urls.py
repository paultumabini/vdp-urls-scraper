from django.urls import path

from . import views

# Must match the second element of ``include(('project.api.urls', app_name), ...)`` in root URLconf.
app_name = 'api'

urlpatterns = [
    path('', views.get_scraped_items, name='api-scraped-items'),
]
