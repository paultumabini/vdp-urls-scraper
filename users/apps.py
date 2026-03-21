from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = "Users App Section"

    def ready(self):
        import users.signals  # noqa

    #! NOTES:
    # The reason the signals are imported here is because Django will not import the signals if you do not import those explicitly. If the signals module is not imported, then the signals are not registered on the corresponding models, and hence if you for example make changes to your User model, the signals will not be triggered.
    # Django recommends doing this way to avoid "side-effects" on how import works
    # noqa = NO-QA (NO Quality Assurance).Adding # noqa to a line indicates that the linter (a program that automatically checks code quality) should not check this line. Any warnings that code may have generated will be ignored.
