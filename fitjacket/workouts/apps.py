from django.apps import AppConfig

class WorkoutsConfig(AppConfig):
    name = 'workouts'

    def ready(self):
        print("→ WorkoutsConfig.ready() running")
        import workouts.signals