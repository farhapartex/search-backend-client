from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        from user.models import User
        try:
            User.ensure_indexes()
        except Exception as e:
            pass
