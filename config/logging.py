# Run before setting the logger anywhere in the code in order for it to report to sentry.
from django.conf import settings
import logging


def setup_logger():
    # Check if in production mode
    if settings.PRODUCTION:
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging

        handler = SentryHandler(settings.SENTRY_DSN)
        handler.setLevel(logging.DEBUG)

        setup_logging(handler)
