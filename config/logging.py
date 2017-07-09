# Run before setting the logger anywhere in the code in order for it to report to sentry.
from django.conf import settings
import logging


def setup_logger():
    if not settings.DEBUG:
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging

        handler = SentryHandler(settings.SENTRY_DSN)
        handler.setLevel(logging.INFO)

        setup_logging(handler)
