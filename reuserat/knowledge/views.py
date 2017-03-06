from django.shortcuts import render
from reuserat.knowledge.models import FAQCategory

def faq_view(request):
    faq_categories = FAQCategory.objects.all()

    return render(request, 'knowledge/questions.html', context={'faq_categories': faq_categories})
