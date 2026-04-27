from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = "Users App Section"

    def ready(self):
        # Import signals at startup so User post_save receivers are registered.
        import users.signals  # noqa
