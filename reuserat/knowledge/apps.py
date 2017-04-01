from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    name = 'reuserat.knowledge'
    verbose_name = "Knowledge"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
