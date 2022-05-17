from django.apps import AppConfig


class PrintConfig(AppConfig):
    name = "print"

    def ready(self):
        from print import signals
