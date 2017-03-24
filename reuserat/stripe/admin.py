from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import StripeAccount, Transaction

class StripeAdmin(admin.ModelAdmin):
    model = StripeAccount


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction

#Parameters- model,AdminClass
admin.site.register(StripeAccount, StripeAdmin)
admin.site.register(Transaction, TransactionAdmin)
