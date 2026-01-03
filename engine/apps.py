from django.apps import AppConfig


class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'

    def ready(self):
        from engine.models import SearchHistory
        try:
            SearchHistory.ensure_indexes()
        except Exception as e:
            pass
