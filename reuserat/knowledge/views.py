from django.shortcuts import render

from reuserat.knowledge.models import FAQCategory
import logging

from config.logging import setup_logger


def faq_view(request):
    faq_categories = [category for category in FAQCategory.objects.all() if category.faq_set.exists()]  # Filter out categories without FAQs
    return render(request, 'knowledge/questions.html', context={'faq_categories': faq_categories})
