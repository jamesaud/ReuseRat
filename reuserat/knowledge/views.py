from django.shortcuts import render, HttpResponse
from reuserat.knowledge.models import FAQCategory
from django.conf import settings
import logging


def setup_logger():
    if not settings.DEBUG:
        # new logging code, because the above doesn't work
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging

        handler = SentryHandler(settings.SENTRY_DSN)
        handler.setLevel(logging.INFO)

        setup_logging(handler)


setup_logger()

logger = logging.getLogger(__name__)

def faq_view(request):

    logger.error("FAQS page, this INCERD another fantastic test", exc_info=True)

    faq_categories = [category for category in FAQCategory.objects.all() if category.faq_set.exists()]  # Filter out categories without FAQs
    return render(request, 'knowledge/questions.html', context={'faq_categories': faq_categories})
