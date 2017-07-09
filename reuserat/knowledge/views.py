from django.shortcuts import render, HttpResponse
from reuserat.knowledge.models import FAQCategory
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


def faq_view(request):

    logger.error("FAQS page, this is another fantastic test", exc_info=True)

    faq_categories = [category for category in FAQCategory.objects.all() if category.faq_set.exists()]  # Filter out categories without FAQs
    return render(request, 'knowledge/questions.html', context={'faq_categories': faq_categories})
