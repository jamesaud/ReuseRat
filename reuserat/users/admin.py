# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User
from reuserat.shipments.models import Shipment
from reuserat.stripe.models import StripeAccount



class ShipmentInline(admin.TabularInline):
    model = Shipment
    show_change_link = True
    extra = 0


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class MyUserAdmin(AuthUserAdmin):
    inlines = (ShipmentInline,)

    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
            ('User Profile', {
                 'fields': ('first_name','last_name', 'email', 'phone', 'address', 'payment_type', 'stripe_account')
              }),
    ) + AuthUserAdmin.fieldsets
    list_display = ('email', 'first_name', 'last_name', 'is_superuser')
    search_fields = ['first_name', 'last_name']
