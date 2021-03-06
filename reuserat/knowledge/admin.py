from django.contrib import admin
from .models import FAQ, FAQCategory
from django.forms import TextInput, Textarea
from django.db import models




class FAQAdmin(admin.ModelAdmin):
    model = FAQ
    list_display = ('question', 'categories')

    formfield_overrides = {
        models.CharField: {'widget': Textarea(
            attrs={'rows': 3,
                   'cols': 40,
                   })},
    }

    def categories(self, obj):
        return [category.name for category in obj.category.all()]


class FAQCategoryAdmin(admin.ModelAdmin):
    model = FAQCategory
    list_display = ('name',)


admin.site.register(FAQ, FAQAdmin)
admin.site.register(FAQCategory, FAQCategoryAdmin)
