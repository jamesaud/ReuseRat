from django.shortcuts import render

from reuserat.knowledge.models import FAQCategory
import logging

from config.logging import setup_logger
logger = logging.getLogger(__name__)

def faq_view(request):
    logger.info("In Knowledge FAQs")
    faq_categories = [category for category in FAQCategory.objects.all() if category.faq_set.exists()]  # Filter out categories without FAQs
    return render(request, 'knowledge/questions.html', context={'faq_categories': faq_categories})
