from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    verbose_name = 'Authentication'

    def ready(self):
        """
        Import signal handlers and perform other app initialization
        """
        # Import signals here if you have any
        # import authentication.signals
        pass

