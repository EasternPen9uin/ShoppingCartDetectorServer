from django.apps import AppConfig

class YoloConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'yolo'
    def ready(self):
        import os
        canRunCron = os.environ.get('RUN_CRON') == "true"
        if not canRunCron: 
            return
        from yolo.cron import main
        main()