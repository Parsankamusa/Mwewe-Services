from django.apps import AppConfig


class AutomationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automations'
    verbose_name = 'Automations Management'

    def ready(self):
        """
        Import signal handlers and perform other app initialization
        """
        # Import signals here if you have any
        # import automations.signals
        pass



