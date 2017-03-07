from django.db import models
from reuserat.users.models import User




class FAQCategory(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class FAQ(models.Model):
    category = models.ManyToManyField(FAQCategory)
    question =  models.CharField(max_length=250)
    answer = models.CharField(max_length=1000)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # Increase the text box size for answer field


    def __str__(self):
        return self.question
