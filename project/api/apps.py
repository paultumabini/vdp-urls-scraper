from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project.api'
    verbose_name = "Listed Auth Tokens"  # default `Api` which is the app name or `Auth Token` if not custom token admin
