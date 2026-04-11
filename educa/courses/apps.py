from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        from educa.redisboard_db_fix import apply_redisboard_db_fix

        apply_redisboard_db_fix()

