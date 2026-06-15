from django.apps import AppConfig


class KniConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kni'

    def ready(self):
        import kni.signals