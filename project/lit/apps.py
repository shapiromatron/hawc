from django.apps import AppConfig

class LitConfig(AppConfig):
    name = 'lit'
    verbose_name = 'Literature'

    def ready(self):
        import signals
