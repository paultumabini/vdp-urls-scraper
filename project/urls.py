from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import (SiteCreateView, SiteDeleteView, SiteDetailView,
                    SiteListView, SiteUpdateView)

urlpatterns = [
    path('', views.home, name='home'),
    path('project/<project_name>/', SiteListView.as_view(), name='site-list'),
    path('project/<project_name>/<str:pk>/', SiteDetailView.as_view(), name='site-detail'),
    path('scrape/new/', SiteCreateView.as_view(), name='new-scrape'),
    path('project/<project_name>/<str:pk>/update', SiteUpdateView.as_view(), name='update-scrape'),
    path('project/<project_name>/<site>/<str:pk>/delete', SiteDeleteView.as_view(), name='delete-scrape'),
    path('api-docs/', views.api_docs, name='api-docs'),
    path('help/', views.help, name='help'),
    path('scrape-data-json/', views.scrape_data_json, name='scrape-json'),
    path('spider-log-json/', views.spider_logs_json, name='log-json'),
    path('web-provider-json/', views.web_providers_json, name='log-json'),
    path('aim-dealer-provider-json/', views.aim_dealers_list, name='aim-dealer-json'),
    path('project/<project_name>/export_scrape_by_csv', views.scrape_data_csv, name='scrape-csv'),
    # path('api/scraped-items/', views.test_api, name='test'),
]


# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
