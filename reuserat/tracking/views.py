from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render




def tracking_schedule_pickup(request, next):
    tracking_pages = ['third_party/ad_conversion_tags/facebook_ads/_lead.html',
                      'third_party/ad_conversion_tags/google_ads/_schedule_booking.html']

    return render(request, 'third_party/redirect_tracking.html',
                  context={'redirect_url': next,
                           'tracking_pages': tracking_pages})

