from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import StripeAccount

class StripeAdmin(admin.ModelAdmin):
    model = StripeAccount

#Parameters- model,AdminClass
admin.site.register(StripeAccount, StripeAdmin)
