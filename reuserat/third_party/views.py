from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def thank_you_for_booking_boxes(request):
    info = request.GET
    print(info)
    context = {'start': info.get('start'),
               'address': info.get('address'),
               'fname': info.get('fname'),
               'lname': info.get('lname'),
               'phone': info.get('phone'),
               'email': info.get('email'),
               'boxes': info.get('boxes'),
               'text': "Thanks For Booking Your Box Delivery!",
               'end': info.get('end'),
               'type': 'boxes',
               }

    return render(request, 'third_party/thanks-for-booking.html', context=context)

def thank_you_for_booking_pickup(request):
    info = request.GET
    print(info)
    context = {'start': info.get('start'),
               'address': info.get('address'),
               'fname': info.get('fname'),
               'lname': info.get('lname'),
               'phone': info.get('phone'),
               'email': info.get('email'),
               'text': "Thanks For Booking Your Pick Up!",
               'end': info.get('end'),
               'type': 'pickup',
               }

    return render(request, 'third_party/thanks-for-booking.html', context=context)
