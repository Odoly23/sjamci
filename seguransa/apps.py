from django.apps import AppConfig


class SeguransaConfig(AppConfig):
    name = 'seguransa'
    verbose_name = 'Seguransa no Auditoria'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals  # noqa: F401
