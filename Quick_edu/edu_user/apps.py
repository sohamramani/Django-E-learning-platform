from django.apps import AppConfig


class EduUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'edu_user'
    def ready(self):
        import edu_user.signals