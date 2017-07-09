from django.shortcuts import render

from config.logging import setup_logger
from reuserat.knowledge.models import FAQCategory


setup_logger()
logger = logging.getLogger(__name__)

def faq_view(request):

    logger.error("FAQS page, this really great another fantastic test", exc_info=True)

    faq_categories = [category for category in FAQCategory.objects.all() if category.faq_set.exists()]  # Filter out categories without FAQs
    return render(request, 'knowledge/questions.html', context={'faq_categories': faq_categories})
