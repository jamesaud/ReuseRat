"""
Processors to be included in every all of the project.
"""
from django.conf import settings

def variables(request):
    """Include variables in templates from settings.py"""
    return {'EXTERNAL_URLS': settings.EXTERNAL_URLS}

